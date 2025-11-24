"""
Pytest fixtures for logz tests
"""

import gzip
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List

import pytest


@pytest.fixture
def sample_log_lines():
    """Sample log lines for testing"""
    return [
        "2025-11-20 17:45:32 INFO Starting application",
        "2025-11-20 17:45:33 DEBUG Loading configuration",
        "2025-11-20 17:45:34 WARN Configuration file not found",
        "2025-11-20 17:45:35 ERROR Failed to connect to database",
        "2025-11-20 17:45:36 CRITICAL System shutdown initiated",
        "2025-11-20 18:00:00 INFO Application restarted",
    ]


@pytest.fixture
def sample_log_file(tmp_path, sample_log_lines):
    """Create a temporary log file with sample content"""
    log_file = tmp_path / "test.log"
    log_file.write_text("\n".join(sample_log_lines))
    return log_file


@pytest.fixture
def sample_log_file_gz(tmp_path, sample_log_lines):
    """Create a temporary gzipped log file"""
    log_file = tmp_path / "test.log.gz"
    with gzip.open(log_file, "wt", encoding="utf-8") as f:
        f.write("\n".join(sample_log_lines))
    return log_file


@pytest.fixture
def sample_log_dir(tmp_path, sample_log_lines):
    """Create a temporary directory with multiple log files"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    # Create multiple log files
    (log_dir / "app1.log").write_text("\n".join(sample_log_lines[:3]))
    (log_dir / "app2.log").write_text("\n".join(sample_log_lines[3:]))

    # Create a subdirectory with another log
    sub_dir = log_dir / "archived"
    sub_dir.mkdir()
    (sub_dir / "old.log").write_text(sample_log_lines[0])

    return log_dir


@pytest.fixture
def empty_log_file(tmp_path):
    """Create an empty log file"""
    log_file = tmp_path / "empty.log"
    log_file.touch()
    return log_file


@pytest.fixture
def log_lines_without_timestamps():
    """Log lines without timestamps"""
    return [
        "Simple log line without timestamp",
        "Another line with no date",
        "ERROR Something went wrong",
    ]


@pytest.fixture
def log_lines_with_custom_format():
    """Log lines with custom date format"""
    return [
        "20/11/2025-17:45:32 INFO Starting application",
        "20/11/2025-17:45:33 DEBUG Loading configuration",
        "20/11/2025-17:45:34 ERROR Failed to start",
    ]


@pytest.fixture
def custom_date_format():
    """Custom date format for testing"""
    return "%d/%m/%Y-%H:%M:%S"
