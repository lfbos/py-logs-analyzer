#!/usr/bin/env python3
import random
import gzip
import click
from datetime import datetime, timedelta

LEVELS = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
MESSAGES = [
    "User logged in",
    "Connection timeout",
    "Database connection established",
    "File not found",
    "Cache miss",
    "Background job started",
    "Background job completed",
    "Rate limit exceeded",
    "Invalid user input",
    "External API unreachable",
]

@click.command()
@click.option("--lines", default=10_000, show_default=True, help="Number of log lines to generate.")
@click.option("--out", default="generated.log", show_default=True, help="Output log file path.")
@click.option("--gz", is_flag=True, help="Compress output as .gz file.")
@click.option("--date-format", default="%Y-%m-%d %H:%M:%S", show_default=True,
              help="Datetime format for each log entry.")
def generate(lines, out, gz, date_format):
    """Generate synthetic logs for testing."""
    start = datetime.now() - timedelta(minutes=10)
    current = start

    if gz:
        f = gzip.open(out, "wt", encoding="utf-8")
    else:
        f = open(out, "w", encoding="utf-8")

    with f:
        for _ in range(lines):
            # time increments
            current += timedelta(milliseconds=random.randint(1, 50))

            # choose fields
            level = random.choice(LEVELS)
            msg = random.choice(MESSAGES)
            user_id = random.randint(1, 5000)

            # render
            timestamp = current.strftime(date_format)
            line = f"{timestamp} [{level}] {msg} user_id={user_id}"

            f.write(line + "\n")

    print(f"Generated {lines} lines → {out}" + (" (gzipped)" if gz else ""))

if __name__ == "__main__":
    generate()
