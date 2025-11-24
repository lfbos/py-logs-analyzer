# Tests for logz

This directory contains the test suite for the logz log analyzer CLI tool.

## Test Structure

- `conftest.py` - Pytest fixtures used across all tests
- `test_log_line.py` - Tests for the LogLine class
- `test_parsing.py` - Tests for parsing functions (parse_timestamp, detect_level, iter_log_lines)
- `test_filters.py` - Tests for LogFilters class and build_filters function
- `test_stats.py` - Tests for LogStats class
- `test_cli.py` - Tests for CLI commands (analyze, stats, tail)

## Running the Tests

### Install dependencies

First, sync the development dependencies using `uv`:

```bash
uv sync --extra dev
```

### Run all tests

```bash
uv run pytest
```

### Run tests with coverage

```bash
uv run pytest --cov=cli --cov-report=html
```

This will generate a coverage report in `htmlcov/index.html`.

### Run specific test files

```bash
uv run pytest tests/test_filters.py
```

### Run specific test classes or functions

```bash
uv run pytest tests/test_filters.py::TestLogFilters::test_filters_from_timestamp
```

### Run tests matching a pattern

```bash
uv run pytest -k "timestamp"
```

### Run tests with verbose output

```bash
uv run pytest -v
```

### Run tests and stop at first failure

```bash
uv run pytest -x
```

## Test Coverage

The test suite aims to cover:

- Core data structures (LogLine, LogFilters, LogStats)
- Parsing functions (timestamp parsing, level detection)
- File I/O operations (reading from files, directories, stdin, gzipped files)
- Filtering logic (timestamp ranges, level filters, substring and regex matching)
- Statistics collection (line counts, level distribution, per-hour aggregation)
- CLI commands (analyze, stats, tail)
- Edge cases (empty files, invalid inputs, missing data)

## Writing New Tests

When adding new tests, follow these guidelines:

1. Use the fixtures defined in `conftest.py` for sample data
2. Group related tests in classes with descriptive names (e.g., `TestParseTimestamp`)
3. Use descriptive test function names that explain what is being tested
4. Each test should focus on a single behavior or scenario
5. Use assertions that clearly indicate what is expected
6. Test both happy paths and edge cases

## Continuous Integration

The tests are designed to run in CI/CD pipelines. Make sure all tests pass before committing changes.

