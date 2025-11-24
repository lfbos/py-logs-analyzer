import gzip
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional, TextIO, Dict, List, Tuple

import click

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"  # e.g. 2025-11-20 17:45:32


# -----------------------------
# Core data structures
# -----------------------------


class LogLine:
    """Represents a single log line plus optional parsed metadata."""

    def __init__(
        self,
        source: str,
        raw: str,
        timestamp: Optional[datetime] = None,
        level: Optional[str] = None,
    ) -> None:
        self.source = source
        self.raw = raw
        self.timestamp = timestamp
        self.level = level


# -----------------------------
# Input handling
# -----------------------------


def iter_files(path: Optional[str]) -> Iterator[Tuple[str, TextIO]]:
    """
    Yield (source_name, file_obj) pairs from:
    - A single file
    - A directory (recursively)
    - Stdin (if path is None or '-')
    Supports .gz files transparently.
    """
    if path is None or path == "-":
        # Read from stdin
        yield ("<stdin>", sys.stdin)
        return

    p = Path(path)

    if p.is_dir():
        for file_path in p.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix == ".gz":
                f = gzip.open(file_path, mode="rt", encoding="utf-8", errors="replace")
            else:
                f = file_path.open("r", encoding="utf-8", errors="replace")
            yield (str(file_path), f)
            f.close()
    else:
        # Single file
        if p.suffix == ".gz":
            f = gzip.open(p, mode="rt", encoding="utf-8", errors="replace")
        else:
            f = p.open("r", encoding="utf-8", errors="replace")
        try:
            yield (str(p), f)
        finally:
            f.close()


def parse_timestamp(line: str, date_format: str) -> Optional[datetime]:
    """
    Try to parse a timestamp at the beginning of the line using the given date_format.
    This is heuristic, but good enough for many real-world logs.
    """
    # We try increasing slices and keep the longest valid match
    max_len = min(len(line), 40)  # arbitrary cap
    last_valid = None
    for end in range(10, max_len + 1):
        candidate = line[:end].strip()
        try:
            last_valid = datetime.strptime(candidate, date_format)
        except ValueError:
            # If we had a valid match before and now it fails, return the last valid one
            if last_valid is not None:
                return last_valid
            continue
    return last_valid


def detect_level(line: str) -> Optional[str]:
    """
    Try to detect a log level by common tokens.
    This is very naive but works for many simple logs.
    """
    upper = line.upper()
    for lvl in ("DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"):
        if lvl in upper:
            return "WARN" if lvl == "WARNING" else lvl
    return None


def iter_log_lines(
    path: Optional[str],
    date_format: str,
) -> Iterator[LogLine]:
    """
    High-level generator that yields LogLine objects from the given path or stdin.
    """
    # We reopen files here to avoid closing them early; iter_files is more of a locator.
    if path is None or path == "-":
        for raw in sys.stdin:
            raw = raw.rstrip("\n")
            ts = parse_timestamp(raw, date_format)
            level = detect_level(raw)
            yield LogLine("<stdin>", raw, ts, level)
        return

    p = Path(path)

    files: List[Path] = []
    if p.is_dir():
        files = [f for f in p.rglob("*") if f.is_file()]
    else:
        files = [p]

    for file_path in files:
        if file_path.suffix == ".gz":
            f = gzip.open(file_path, mode="rt", encoding="utf-8", errors="replace")
        else:
            f = file_path.open("r", encoding="utf-8", errors="replace")

        try:
            for raw in f:
                raw = raw.rstrip("\n")
                ts = parse_timestamp(raw, date_format)
                level = detect_level(raw)
                yield LogLine(str(file_path), raw, ts, level)
        finally:
            f.close()


# -----------------------------
# Filtering
# -----------------------------


class LogFilters:
    """Bundle of filters applied to LogLine objects."""

    def __init__(
        self,
        from_ts: Optional[datetime] = None,
        to_ts: Optional[datetime] = None,
        levels: Optional[List[str]] = None,
        match: Optional[str] = None,
        regex: Optional[re.Pattern] = None,
    ) -> None:
        self.from_ts = from_ts
        self.to_ts = to_ts
        self.levels = [lvl.upper() for lvl in levels] if levels else None
        self.match = match
        self.regex = regex

    def keep(self, line: LogLine) -> bool:
        """Return True if the line passes all filters."""
        # Date range
        if self.from_ts or self.to_ts:
            if line.timestamp is None:
                return False
            if self.from_ts and line.timestamp < self.from_ts:
                return False
            if self.to_ts and line.timestamp > self.to_ts:
                return False

        # Levels
        if self.levels:
            if line.level is None:
                return False
            if line.level.upper() not in self.levels:
                return False

        # Substring match
        if self.match and self.match not in line.raw:
            return False

        # Regex
        if self.regex and not self.regex.search(line.raw):
            return False

        return True


def build_filters(
    from_str: Optional[str],
    to_str: Optional[str],
    date_format: str,
    levels: List[str],
    match: Optional[str],
    regex: Optional[str],
) -> LogFilters:
    from_ts = datetime.strptime(from_str, date_format) if from_str else None
    to_ts = datetime.strptime(to_str, date_format) if to_str else None
    compiled_regex = re.compile(regex) if regex else None
    return LogFilters(
        from_ts=from_ts,
        to_ts=to_ts,
        levels=levels or None,
        match=match,
        regex=compiled_regex,
    )


# -----------------------------
# Stats
# -----------------------------


class LogStats:
    """Collects simple statistics from log lines."""

    def __init__(self) -> None:
        self.total_lines = 0
        self.level_counts: Dict[str, int] = {}
        self.per_hour_counts: Dict[str, int] = {}

    def add(self, line: LogLine) -> None:
        self.total_lines += 1

        if line.level:
            lvl = line.level.upper()
            self.level_counts[lvl] = self.level_counts.get(lvl, 0) + 1

        if line.timestamp:
            hour_key = line.timestamp.strftime("%Y-%m-%d %H:00")
            self.per_hour_counts[hour_key] = self.per_hour_counts.get(hour_key, 0) + 1

    def to_dict(self) -> Dict[str, object]:
        return {
            "total_lines": self.total_lines,
            "levels": self.level_counts,
            "per_hour": self.per_hour_counts,
        }


# -----------------------------
# CLI
# -----------------------------


@click.group()
def cli() -> None:
    """logz: A simple yet powerful log analyzer CLI."""
    pass


common_options = [
    click.option(
        "--date-format",
        default=DEFAULT_DATE_FORMAT,
        show_default=True,
        help="Datetime format used at the beginning of the log line.",
    ),
    click.option(
        "--from-ts",
        "from_ts",
        default=None,
        help="Lower bound datetime filter (uses --date-format).",
    ),
    click.option(
        "--to-ts",
        "to_ts",
        default=None,
        help="Upper bound datetime filter (uses --date-format).",
    ),
    click.option(
        "--level",
        "levels",
        multiple=True,
        help="Log levels to include (can be passed multiple times).",
    ),
    click.option(
        "--match",
        default=None,
        help="Substring to match.",
    ),
    click.option(
        "--regex",
        default=None,
        help="Regular expression to match.",
    ),
]


def apply_common_options(func):
    """Decorator to apply shared filtering options to subcommands."""
    for opt in reversed(common_options):
        func = opt(func)
    return func


@cli.command()
@click.argument("path", required=False)
@apply_common_options
@click.option(
    "--out",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True),
    default=None,
    help="Output file to write filtered lines. If omitted, prints to stdout.",
)
def analyze(
    path: Optional[str],
    date_format: str,
    from_ts: Optional[str],
    to_ts: Optional[str],
    levels: List[str],
    match: Optional[str],
    regex: Optional[str],
    out: Optional[str],
) -> None:
    """
    Filter and print log lines from PATH (file/dir) or stdin.
    """
    filters = build_filters(from_ts, to_ts, date_format, levels, match, regex)
    lines = iter_log_lines(path, date_format)

    if out:
        out_path = Path(out)
        with out_path.open("w", encoding="utf-8") as f:
            for line in lines:
                if filters.keep(line):
                    f.write(line.raw + "\n")
    else:
        for line in lines:
            if filters.keep(line):
                click.echo(line.raw)


@cli.command()
@click.argument("path", required=False)
@apply_common_options
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "markdown"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Output format for stats.",
)
def stats(
    path: Optional[str],
    date_format: str,
    from_ts: Optional[str],
    to_ts: Optional[str],
    levels: List[str],
    match: Optional[str],
    regex: Optional[str],
    fmt: str,
) -> None:
    """
    Compute statistics for log lines from PATH (file/dir) or stdin.
    """
    import json

    filters = build_filters(from_ts, to_ts, date_format, levels, match, regex)
    lines = iter_log_lines(path, date_format)

    stats_obj = LogStats()
    for line in lines:
        if filters.keep(line):
            stats_obj.add(line)

    data = stats_obj.to_dict()

    if fmt.lower() == "json":
        click.echo(json.dumps(data, indent=2))
    else:
        # Simple markdown rendering
        click.echo("# Log Statistics")
        click.echo()
        click.echo(f"- Total lines: **{data['total_lines']}**")
        click.echo()
        click.echo("## Levels")
        for lvl, count in data["levels"].items():
            click.echo(f"- **{lvl}**: {count}")
        click.echo()
        click.echo("## Per hour")
        for hour, count in data["per_hour"].items():
            click.echo(f"- {hour}: {count}")


@cli.command()
@click.argument("path", required=True)
@apply_common_options
@click.option(
    "--interval",
    type=float,
    default=0.5,
    show_default=True,
    help="Polling interval in seconds.",
)
@click.option(
    "--from-start",
    is_flag=True,
    help="If set, start reading from the beginning instead of the end.",
)
def tail(
    path: str,
    date_format: str,
    from_ts: Optional[str],
    to_ts: Optional[str],
    levels: List[str],
    match: Optional[str],
    regex: Optional[str],
    interval: float,
    from_start: bool,
) -> None:
    """
    Tail a single log file, similar to `tail -f`, with filters applied.
    """
    filters = build_filters(from_ts, to_ts, date_format, levels, match, regex)
    file_path = Path(path)

    if not file_path.is_file():
        raise click.ClickException(f"{path} is not a valid file")

    # Note: we don't support .gz for tail, on purpose.
    with file_path.open("r", encoding="utf-8", errors="replace") as f:
        if not from_start:
            # Seek to the end of file
            f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                # No new data yet
                time.sleep(interval)
                continue

            raw = line.rstrip("\n")
            ts = parse_timestamp(raw, date_format)
            level = detect_level(raw)
            log_line = LogLine(str(file_path), raw, ts, level)

            if filters.keep(log_line):
                click.echo(raw)


if __name__ == "__main__":
    cli()
