# Python Logs Analyzer

A simple yet powerful log analyzer CLI tool written in Python.

## Features

- **Multiple input sources**: Read from files, directories (recursive), gzipped files, or stdin
- **Flexible filtering**:
  - Date range filtering (from/to timestamps)
  - Log level filtering (DEBUG, INFO, WARN, ERROR, CRITICAL)
  - Substring matching
  - Regular expression matching
- **Statistics generation**: Get insights about log levels and per-hour distribution
- **Tail mode**: Monitor log files in real-time like `tail -f`
- **Multiple output formats**: JSON or Markdown for statistics

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone <repository-url>
cd logz

# Install dependencies
uv sync

# Install with development dependencies (includes pytest)
uv sync --extra dev
```

## Usage

📖 **For comprehensive examples of all command combinations, see [EXAMPLES.md](EXAMPLES.md)**

### Quick Start Examples

### Analyze Command

Filter and print log lines from a file, directory, or stdin.

**Note**: If you run `analyze` without specifying a PATH, it will read from stdin (standard input). You'll see a message indicating it's waiting for input. Press Ctrl+D to finish or Ctrl+C to cancel.

```bash
# Analyze a single log file
uv run logz analyze app.log

# Analyze all logs in a directory (recursive)
uv run logz analyze /var/log/myapp/

# Filter by log level
uv run logz analyze app.log --level ERROR --level CRITICAL

# Filter by date range
uv run logz analyze app.log --from-ts "2025-11-20 10:00:00" --to-ts "2025-11-20 18:00:00"

# Filter by substring
uv run logz analyze app.log --match "database"

# Filter by regex
uv run logz analyze app.log --regex "error \d+"

# Combine filters
uv run logz analyze app.log --level ERROR --match "database" --from-ts "2025-11-20 10:00:00"

# Save output to file
uv run logz analyze app.log --level ERROR --out errors.log

# Read from stdin (pipe from another command)
cat app.log | uv run logz analyze

# Read from stdin (interactive - type or paste logs, then press Ctrl+D)
uv run logz analyze
# ... paste your logs here ...
# Press Ctrl+D when done
```

### Stats Command

Compute statistics about your log files.

```bash
# Get statistics in JSON format
uv run logz stats app.log

# Get statistics in Markdown format
uv run logz stats app.log --format markdown

# Statistics with filters
uv run logz stats app.log --level ERROR --from-ts "2025-11-20 10:00:00"

# Statistics from directory
uv run logz stats /var/log/myapp/
```

### Tail Command

Monitor a log file in real-time with filtering.

```bash
# Tail a log file (like tail -f)
uv run logz tail app.log

# Start reading from the beginning
uv run logz tail app.log --from-start

# Tail with filters
uv run logz tail app.log --level ERROR

# Custom polling interval (default: 0.5 seconds)
uv run logz tail app.log --interval 1.0
```

## Custom Date Formats

By default, logz expects timestamps in the format `YYYY-MM-DD HH:MM:SS`. You can specify a custom format:

```bash
# Custom date format
uv run logz analyze app.log --date-format "%d/%m/%Y-%H:%M:%S"
```

## Supported Log Levels

- DEBUG
- INFO
- WARN / WARNING (normalized to WARN)
- ERROR
- CRITICAL

## Examples

### Example 1: Find all errors in the last hour

```bash
uv run logz analyze app.log \
  --level ERROR \
  --from-ts "2025-11-24 10:00:00" \
  --to-ts "2025-11-24 11:00:00"
```

### Example 2: Get hourly statistics for warnings and errors

```bash
uv run logz stats app.log \
  --level WARN \
  --level ERROR \
  --format markdown
```

### Example 3: Monitor production logs for critical issues

```bash
uv run logz tail /var/log/production.log \
  --level CRITICAL \
  --level ERROR
```

### Example 4: Analyze compressed logs

```bash
uv run logz analyze logs/archive.log.gz --level ERROR
```

## Development

### Running Tests

This project includes a comprehensive test suite with pytest.

```bash
# Install development dependencies
uv sync --extra dev

# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=cli --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=cli --cov-report=html
# Open htmlcov/index.html in your browser

# Run specific test file
uv run pytest tests/test_filters.py

# Run specific test class or function
uv run pytest tests/test_filters.py::TestLogFilters::test_filters_from_timestamp

# Run tests matching a pattern
uv run pytest -k "timestamp"

# Run tests and stop at first failure
uv run pytest -x
```

### Test Coverage

Current test coverage: **99%**

The test suite includes:
- 100 test cases covering all major functionality
- Unit tests for parsing functions, filters, and statistics
- Integration tests for CLI commands
- Tests for edge cases and error handling

Test files:
- `tests/test_log_line.py` - LogLine class tests
- `tests/test_parsing.py` - Parsing functions tests
- `tests/test_filters.py` - Filtering logic tests
- `tests/test_stats.py` - Statistics collection tests
- `tests/test_cli.py` - CLI commands tests
- `tests/test_iter_files.py` - File iteration tests
- `tests/conftest.py` - Shared pytest fixtures

### Project Structure

```
logz/
├── cli.py              # Main application code
├── pyproject.toml      # Project configuration and dependencies
├── pytest.ini          # Pytest configuration
├── README.md           # This file
├── tests/
│   ├── __init__.py
│   ├── conftest.py     # Pytest fixtures
│   ├── test_cli.py
│   ├── test_filters.py
│   ├── test_iter_files.py
│   ├── test_log_line.py
│   ├── test_parsing.py
│   ├── test_stats.py
│   └── README.md       # Test documentation
└── htmlcov/            # Coverage reports (generated)
```

## Requirements

- Python >= 3.13
- click >= 8.3.1

### Development Requirements

- pytest >= 9.0.0
- pytest-cov >= 7.0.0
