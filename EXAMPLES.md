# logz - Complete Usage Examples

This document contains comprehensive examples for all commands and option combinations.

## Table of Contents
- [Analyze Command](#analyze-command)
- [Stats Command](#stats-command)
- [Tail Command](#tail-command)

---

## Analyze Command

The `analyze` command filters and prints log lines with various filtering options.

### Basic Usage

```bash
# Read from a single file
uv run logz analyze my.log

# Read from a directory (recursive)
uv run logz analyze /path/to/logs/

# Read from gzipped file
uv run logz analyze archive.log.gz

# Read from stdin (pipe)
cat my.log | uv run logz analyze

# Read from stdin (interactive - you type, then Ctrl+D)
uv run logz analyze
```

### Filter by Log Level

```bash
# Single level
uv run logz analyze my.log --level ERROR
uv run logz analyze my.log --level DEBUG
uv run logz analyze my.log --level INFO
uv run logz analyze my.log --level WARN
uv run logz analyze my.log --level CRITICAL

# Multiple levels
uv run logz analyze my.log --level ERROR --level CRITICAL
uv run logz analyze my.log --level WARN --level ERROR --level CRITICAL
uv run logz analyze my.log --level DEBUG --level INFO
```

### Filter by Date/Time Range

```bash
# From timestamp (everything after)
uv run logz analyze my.log --from-ts "2025-11-23 19:00:00"

# To timestamp (everything before)
uv run logz analyze my.log --to-ts "2025-11-23 20:00:00"

# Date range (between two timestamps)
uv run logz analyze my.log --from-ts "2025-11-23 19:00:00" --to-ts "2025-11-23 20:00:00"

# Last hour
uv run logz analyze my.log --from-ts "2025-11-23 19:00:00" --to-ts "2025-11-23 20:00:00"

# Specific minute
uv run logz analyze my.log --from-ts "2025-11-23 19:26:55" --to-ts "2025-11-23 19:26:56"
```

### Custom Date Format

```bash
# Custom date format: DD/MM/YYYY-HH:MM:SS
uv run logz analyze custom.log --date-format "%d/%m/%Y-%H:%M:%S"

# Custom date format: YYYY-MM-DD HH:MM:SS.mmm
uv run logz analyze custom.log --date-format "%Y-%m-%d %H:%M:%S.%f"

# Custom date format with timezone: YYYY-MM-DDTHH:MM:SS
uv run logz analyze custom.log --date-format "%Y-%m-%dT%H:%M:%S"

# Filter with custom date format
uv run logz analyze custom.log \
  --date-format "%d/%m/%Y-%H:%M:%S" \
  --from-ts "23/11/2025-19:00:00"
```

### Filter by Substring Match

```bash
# Match "database"
uv run logz analyze my.log --match "database"

# Match "timeout"
uv run logz analyze my.log --match "timeout"

# Match "user_id=123"
uv run logz analyze my.log --match "user_id=123"

# Match case-sensitive (note: --match is case-sensitive)
uv run logz analyze my.log --match "ERROR"
```

### Filter by Regular Expression

```bash
# Match user_id with specific numbers
uv run logz analyze my.log --regex "user_id=[0-9]{4}"

# Match ERROR or CRITICAL
uv run logz analyze my.log --regex "\[ERROR\]|\[CRITICAL\]"

# Match specific user_id range (1000-1999)
uv run logz analyze my.log --regex "user_id=1[0-9]{3}"

# Match lines with "timeout" or "unreachable"
uv run logz analyze my.log --regex "timeout|unreachable"

# Match IP addresses
uv run logz analyze my.log --regex "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"

# Match email addresses
uv run logz analyze my.log --regex "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
```

### Output to File

```bash
# Save to file
uv run logz analyze my.log --level ERROR --out errors.log

# Save filtered results
uv run logz analyze my.log \
  --from-ts "2025-11-23 19:00:00" \
  --level ERROR \
  --level CRITICAL \
  --out critical_errors.log
```

### Combined Filters (2 options)

```bash
# Level + substring
uv run logz analyze my.log --level ERROR --match "database"

# Level + regex
uv run logz analyze my.log --level CRITICAL --regex "user_id=[0-9]+"

# Level + time range
uv run logz analyze my.log \
  --level ERROR \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00"

# Substring + time range
uv run logz analyze my.log \
  --match "timeout" \
  --from-ts "2025-11-23 19:00:00"

# Regex + time range
uv run logz analyze my.log \
  --regex "user_id=1[0-9]{3}" \
  --from-ts "2025-11-23 19:00:00"
```

### Combined Filters (3 options)

```bash
# Level + substring + time range
uv run logz analyze my.log \
  --level ERROR \
  --match "database" \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00"

# Level + regex + time range
uv run logz analyze my.log \
  --level ERROR \
  --regex "user_id=[0-9]{4}" \
  --from-ts "2025-11-23 19:00:00"

# Multiple levels + substring + time range
uv run logz analyze my.log \
  --level ERROR \
  --level CRITICAL \
  --match "timeout" \
  --from-ts "2025-11-23 19:00:00"

# Level + substring + output file
uv run logz analyze my.log \
  --level ERROR \
  --match "database" \
  --out db_errors.log
```

### Combined Filters (4+ options)

```bash
# Level + substring + time range + output
uv run logz analyze my.log \
  --level ERROR \
  --level CRITICAL \
  --match "database" \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00" \
  --out critical_db_errors.log

# Level + regex + time range + output
uv run logz analyze my.log \
  --level ERROR \
  --regex "user_id=(1[0-9]{3}|2[0-9]{3})" \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00" \
  --out specific_users_errors.log

# All options combined
uv run logz analyze my.log \
  --date-format "%Y-%m-%d %H:%M:%S" \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00" \
  --level ERROR \
  --level CRITICAL \
  --match "database" \
  --out filtered_output.log
```

### Piping and Chaining

```bash
# Pipe from another command
cat my.log | uv run logz analyze --level ERROR

# Chain multiple filters
uv run logz analyze my.log --level ERROR | grep "database"

# Count filtered lines
uv run logz analyze my.log --level ERROR | wc -l

# Get first 10 errors
uv run logz analyze my.log --level ERROR | head -10

# Get last 10 errors
uv run logz analyze my.log --level ERROR | tail -10

# Search within filtered results
uv run logz analyze my.log --level ERROR | grep "timeout"

# Analyze multiple files
cat file1.log file2.log | uv run logz analyze --level ERROR
```

---

## Stats Command

The `stats` command computes statistics about log files.

### Basic Usage

```bash
# Get stats in JSON format (default)
uv run logz stats my.log

# Get stats in Markdown format
uv run logz stats my.log --format markdown

# Get stats in JSON format (explicit)
uv run logz stats my.log --format json

# Stats from directory
uv run logz stats /path/to/logs/

# Stats from gzipped file
uv run logz stats archive.log.gz

# Stats from stdin
cat my.log | uv run logz stats
```

### Stats with Level Filter

```bash
# Stats for ERROR only
uv run logz stats my.log --level ERROR

# Stats for ERROR in Markdown
uv run logz stats my.log --level ERROR --format markdown

# Stats for multiple levels
uv run logz stats my.log --level ERROR --level CRITICAL

# Stats for all warning levels
uv run logz stats my.log --level WARN --level ERROR --level CRITICAL --format markdown
```

### Stats with Time Range

```bash
# Stats from a specific time
uv run logz stats my.log --from-ts "2025-11-23 19:00:00"

# Stats until a specific time
uv run logz stats my.log --to-ts "2025-11-23 20:00:00"

# Stats for a time range
uv run logz stats my.log \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00"

# Stats for last hour (Markdown format)
uv run logz stats my.log \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00" \
  --format markdown
```

### Stats with Custom Date Format

```bash
# Custom date format
uv run logz stats custom.log --date-format "%d/%m/%Y-%H:%M:%S"

# Custom format with time range
uv run logz stats custom.log \
  --date-format "%d/%m/%Y-%H:%M:%S" \
  --from-ts "23/11/2025-19:00:00" \
  --to-ts "23/11/2025-20:00:00"
```

### Stats with Substring Filter

```bash
# Stats for lines containing "database"
uv run logz stats my.log --match "database"

# Stats for lines containing "timeout" (JSON)
uv run logz stats my.log --match "timeout" --format json

# Stats for lines containing "timeout" (Markdown)
uv run logz stats my.log --match "timeout" --format markdown
```

### Stats with Regex Filter

```bash
# Stats for specific user_id pattern
uv run logz stats my.log --regex "user_id=[0-9]{4}"

# Stats for ERROR or CRITICAL (via regex)
uv run logz stats my.log --regex "\[ERROR\]|\[CRITICAL\]"

# Stats with regex in Markdown
uv run logz stats my.log --regex "timeout|unreachable" --format markdown
```

### Combined Stats Filters

```bash
# Level + time range
uv run logz stats my.log \
  --level ERROR \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00" \
  --format markdown

# Level + substring
uv run logz stats my.log \
  --level ERROR \
  --match "database" \
  --format json

# Level + regex
uv run logz stats my.log \
  --level CRITICAL \
  --regex "user_id=[0-9]+" \
  --format markdown

# Multiple levels + time range + format
uv run logz stats my.log \
  --level ERROR \
  --level CRITICAL \
  --from-ts "2025-11-23 19:00:00" \
  --format markdown

# Level + substring + time range
uv run logz stats my.log \
  --level ERROR \
  --match "timeout" \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00" \
  --format markdown

# All filters combined
uv run logz stats my.log \
  --date-format "%Y-%m-%d %H:%M:%S" \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00" \
  --level ERROR \
  --level CRITICAL \
  --match "database" \
  --format markdown
```

### Stats Output Piping

```bash
# Pretty print JSON stats
uv run logz stats my.log --format json | python -m json.tool

# Save stats to file
uv run logz stats my.log --format json > stats.json
uv run logz stats my.log --format markdown > stats.md

# Filter stats output
uv run logz stats my.log --format markdown | grep "ERROR"
```

---

## Tail Command

The `tail` command monitors a log file in real-time (like `tail -f`).

### Basic Usage

```bash
# Tail a log file (starts from end)
uv run logz tail my.log

# Tail from the beginning
uv run logz tail my.log --from-start

# Tail with custom interval (default is 0.5 seconds)
uv run logz tail my.log --interval 1.0

# Tail with faster polling
uv run logz tail my.log --interval 0.1

# Tail with slower polling
uv run logz tail my.log --interval 2.0
```

### Tail with Level Filter

```bash
# Only show ERROR logs
uv run logz tail my.log --level ERROR

# Only show CRITICAL logs
uv run logz tail my.log --level CRITICAL

# Show ERROR and CRITICAL
uv run logz tail my.log --level ERROR --level CRITICAL

# Show warnings and above
uv run logz tail my.log --level WARN --level ERROR --level CRITICAL

# Debug logs from start
uv run logz tail my.log --level DEBUG --from-start
```

### Tail with Time Range Filter

```bash
# Only show logs after a specific time
uv run logz tail my.log --from-ts "2025-11-23 19:00:00"

# Only show logs before a specific time (until it reaches that time)
uv run logz tail my.log --to-ts "2025-11-23 20:00:00"

# Show logs in a time range
uv run logz tail my.log \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00"

# Time range from start
uv run logz tail my.log \
  --from-start \
  --from-ts "2025-11-23 19:00:00"
```

### Tail with Custom Date Format

```bash
# Custom date format
uv run logz tail custom.log --date-format "%d/%m/%Y-%H:%M:%S"

# Custom format with filter
uv run logz tail custom.log \
  --date-format "%d/%m/%Y-%H:%M:%S" \
  --from-ts "23/11/2025-19:00:00" \
  --level ERROR
```

### Tail with Substring Filter

```bash
# Only show lines containing "database"
uv run logz tail my.log --match "database"

# Only show lines containing "timeout"
uv run logz tail my.log --match "timeout"

# Match with level filter
uv run logz tail my.log --level ERROR --match "database"

# Match from start
uv run logz tail my.log --match "user_id=123" --from-start
```

### Tail with Regex Filter

```bash
# Show lines matching user_id pattern
uv run logz tail my.log --regex "user_id=[0-9]{4}"

# Show ERROR or CRITICAL via regex
uv run logz tail my.log --regex "\[ERROR\]|\[CRITICAL\]"

# Complex regex pattern
uv run logz tail my.log --regex "timeout|unreachable|failed"

# Regex with level filter
uv run logz tail my.log --level ERROR --regex "database.*connection"
```

### Combined Tail Filters

```bash
# Level + from-start
uv run logz tail my.log --level ERROR --from-start

# Level + interval
uv run logz tail my.log --level ERROR --interval 1.0

# Level + substring
uv run logz tail my.log --level ERROR --match "database"

# Level + regex
uv run logz tail my.log --level CRITICAL --regex "user_id=[0-9]+"

# Level + time filter
uv run logz tail my.log \
  --level ERROR \
  --from-ts "2025-11-23 19:00:00"

# Multiple levels + substring + from-start
uv run logz tail my.log \
  --level ERROR \
  --level CRITICAL \
  --match "timeout" \
  --from-start

# Level + substring + interval
uv run logz tail my.log \
  --level ERROR \
  --match "database" \
  --interval 1.0 \
  --from-start

# All options combined
uv run logz tail my.log \
  --date-format "%Y-%m-%d %H:%M:%S" \
  --from-ts "2025-11-23 19:00:00" \
  --level ERROR \
  --level CRITICAL \
  --match "database" \
  --interval 0.5 \
  --from-start
```

### Tail with Output Redirection

```bash
# Save tail output to file (continues until Ctrl+C)
uv run logz tail my.log --level ERROR > errors_live.log

# Pipe to another command
uv run logz tail my.log --level ERROR | grep "database"

# Count lines as they come
uv run logz tail my.log --level ERROR | wc -l

# Multiple filters with output
uv run logz tail my.log \
  --level ERROR \
  --level CRITICAL \
  --match "timeout" \
  --from-start > critical_timeouts.log
```

---

## Real-World Scenarios

### Scenario 1: Debugging Production Issues

```bash
# Find all errors in the last hour
uv run logz analyze my.log \
  --level ERROR \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00" \
  --out last_hour_errors.log

# Get statistics for those errors
uv run logz stats my.log \
  --level ERROR \
  --from-ts "2025-11-23 19:00:00" \
  --to-ts "2025-11-23 20:00:00" \
  --format markdown

# Monitor for new errors in real-time
uv run logz tail my.log --level ERROR --level CRITICAL
```

### Scenario 2: Database Connection Issues

```bash
# Find all database-related errors
uv run logz analyze my.log \
  --level ERROR \
  --match "database" \
  --out db_errors.log

# Get statistics
uv run logz stats my.log \
  --level ERROR \
  --match "database" \
  --format markdown

# Monitor database errors in real-time
uv run logz tail my.log --match "database" --level ERROR
```

### Scenario 3: User-Specific Issues

```bash
# Find all logs for user_id=1234
uv run logz analyze my.log --match "user_id=1234"

# Find errors for users 1000-1999
uv run logz analyze my.log \
  --level ERROR \
  --regex "user_id=1[0-9]{3}"

# Monitor specific user in real-time
uv run logz tail my.log --match "user_id=1234"
```

### Scenario 4: Performance Analysis

```bash
# Get hourly distribution of all logs
uv run logz stats my.log --format markdown

# Get hourly distribution of errors only
uv run logz stats my.log \
  --level ERROR \
  --level CRITICAL \
  --format markdown

# Analyze timeout patterns
uv run logz stats my.log \
  --match "timeout" \
  --format markdown
```

### Scenario 5: Analyzing Compressed Archives

```bash
# Analyze old compressed logs
uv run logz analyze archive.log.gz --level ERROR

# Get stats from compressed logs
uv run logz stats archive.log.gz --format markdown

# Find specific patterns in compressed logs
uv run logz analyze archive.log.gz \
  --regex "user_id=[0-9]{4}" \
  --level ERROR \
  --out extracted_errors.log
```

### Scenario 6: Multi-File Analysis

```bash
# Analyze entire log directory
uv run logz analyze /var/log/myapp/ --level ERROR

# Get stats from all logs in directory
uv run logz stats /var/log/myapp/ --format markdown

# Find critical issues across all logs
uv run logz analyze /var/log/myapp/ \
  --level CRITICAL \
  --out all_critical.log
```

---

## Tips and Tricks

### Combining with Standard Unix Tools

```bash
# Count errors per hour
uv run logz analyze my.log --level ERROR | cut -d' ' -f2 | cut -d':' -f1 | sort | uniq -c

# Find most common error messages
uv run logz analyze my.log --level ERROR | cut -d']' -f2- | sort | uniq -c | sort -rn | head -10

# Extract unique user IDs from errors
uv run logz analyze my.log --level ERROR | grep -o "user_id=[0-9]*" | sort -u

# Get error rate per minute
uv run logz analyze my.log --level ERROR | cut -d' ' -f1,2 | cut -d':' -f1,2 | sort | uniq -c
```

### Performance Tips

```bash
# For large files, filter early
uv run logz analyze huge.log --level ERROR --from-ts "2025-11-23 19:00:00" > filtered.log

# Use compressed files to save disk space
uv run logz analyze my.log --level ERROR | gzip > errors.log.gz

# Process only what you need
uv run logz analyze my.log --level ERROR --match "database" | head -100
```

### Monitoring Tips

```bash
# Monitor with timestamp
uv run logz tail my.log --level ERROR | while read line; do echo "[$(date)] $line"; done

# Alert on critical logs (example with system notification)
uv run logz tail my.log --level CRITICAL | while read line; do echo "$line"; done

# Save and display simultaneously
uv run logz tail my.log --level ERROR | tee live_errors.log
```

---

## Summary of All Options

### analyze
- `[PATH]` - File, directory, or omit for stdin
- `--date-format TEXT` - Custom date format
- `--from-ts TEXT` - Start timestamp
- `--to-ts TEXT` - End timestamp
- `--level TEXT` - Log level (multiple allowed)
- `--match TEXT` - Substring match
- `--regex TEXT` - Regular expression
- `--out FILE` - Output file

### stats
- `[PATH]` - File, directory, or omit for stdin
- `--date-format TEXT` - Custom date format
- `--from-ts TEXT` - Start timestamp
- `--to-ts TEXT` - End timestamp
- `--level TEXT` - Log level (multiple allowed)
- `--match TEXT` - Substring match
- `--regex TEXT` - Regular expression
- `--format [json|markdown]` - Output format

### tail
- `PATH` - File to tail (required)
- `--date-format TEXT` - Custom date format
- `--from-ts TEXT` - Start timestamp
- `--to-ts TEXT` - End timestamp
- `--level TEXT` - Log level (multiple allowed)
- `--match TEXT` - Substring match
- `--regex TEXT` - Regular expression
- `--interval FLOAT` - Polling interval in seconds
- `--from-start` - Start reading from beginning

---

**Note**: Press `Ctrl+C` to interrupt any running command.

