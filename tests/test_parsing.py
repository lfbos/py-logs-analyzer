"""
Tests for parsing functions (parse_timestamp, detect_level, iter_log_lines)
"""

from datetime import datetime
from pathlib import Path

import pytest

from cli import (DEFAULT_DATE_FORMAT, detect_level, iter_log_lines,
                 parse_timestamp)


class TestParseTimestamp:
    """Tests for parse_timestamp function"""

    def test_parse_timestamp_valid(self):
        """Test parsing a valid timestamp"""
        line = "2025-11-20 17:45:32 INFO Test message"
        result = parse_timestamp(line, DEFAULT_DATE_FORMAT)

        assert result == datetime(2025, 11, 20, 17, 45, 32)

    def test_parse_timestamp_with_extra_content(self):
        """Test parsing timestamp with extra content after it"""
        line = "2025-11-20 17:45:32 This is a very long message with lots of text"
        result = parse_timestamp(line, DEFAULT_DATE_FORMAT)

        assert result == datetime(2025, 11, 20, 17, 45, 32)

    def test_parse_timestamp_custom_format(self, custom_date_format):
        """Test parsing timestamp with custom format"""
        line = "20/11/2025-17:45:32 INFO Test message"
        result = parse_timestamp(line, custom_date_format)

        assert result == datetime(2025, 11, 20, 17, 45, 32)

    def test_parse_timestamp_invalid(self):
        """Test parsing an invalid timestamp returns None"""
        line = "Not a timestamp at all"
        result = parse_timestamp(line, DEFAULT_DATE_FORMAT)

        assert result is None

    def test_parse_timestamp_partial(self):
        """Test parsing a line with incomplete timestamp"""
        line = "2025-11-20"
        result = parse_timestamp(line, DEFAULT_DATE_FORMAT)

        assert result is None

    def test_parse_timestamp_empty_line(self):
        """Test parsing an empty line"""
        result = parse_timestamp("", DEFAULT_DATE_FORMAT)

        assert result is None


class TestDetectLevel:
    """Tests for detect_level function"""

    def test_detect_level_debug(self):
        """Test detecting DEBUG level"""
        line = "2025-11-20 17:45:32 DEBUG Loading configuration"
        result = detect_level(line)

        assert result == "DEBUG"

    def test_detect_level_info(self):
        """Test detecting INFO level"""
        line = "2025-11-20 17:45:32 INFO Starting application"
        result = detect_level(line)

        assert result == "INFO"

    def test_detect_level_warn(self):
        """Test detecting WARN level"""
        line = "2025-11-20 17:45:32 WARN Configuration file not found"
        result = detect_level(line)

        assert result == "WARN"

    def test_detect_level_warning(self):
        """Test detecting WARNING level (converts to WARN)"""
        line = "2025-11-20 17:45:32 WARNING Configuration file not found"
        result = detect_level(line)

        assert result == "WARN"

    def test_detect_level_error(self):
        """Test detecting ERROR level"""
        line = "2025-11-20 17:45:32 ERROR Failed to connect"
        result = detect_level(line)

        assert result == "ERROR"

    def test_detect_level_critical(self):
        """Test detecting CRITICAL level"""
        line = "2025-11-20 17:45:32 CRITICAL System failure"
        result = detect_level(line)

        assert result == "CRITICAL"

    def test_detect_level_lowercase(self):
        """Test detecting level in lowercase"""
        line = "2025-11-20 17:45:32 info Starting application"
        result = detect_level(line)

        assert result == "INFO"

    def test_detect_level_mixed_case(self):
        """Test detecting level in mixed case"""
        line = "2025-11-20 17:45:32 ErRoR Failed to connect"
        result = detect_level(line)

        assert result == "ERROR"

    def test_detect_level_none(self):
        """Test detecting no level returns None"""
        line = "2025-11-20 17:45:32 Just a regular message"
        result = detect_level(line)

        assert result is None

    def test_detect_level_in_message_body(self):
        """Test detecting level when it appears in message body"""
        line = "The ERROR occurred in the database"
        result = detect_level(line)

        assert result == "ERROR"


class TestIterLogLines:
    """Tests for iter_log_lines function"""

    def test_iter_log_lines_from_file(self, sample_log_file):
        """Test iterating log lines from a file"""
        lines = list(iter_log_lines(str(sample_log_file), DEFAULT_DATE_FORMAT))

        assert len(lines) == 6
        assert lines[0].source == str(sample_log_file)
        assert lines[0].level == "INFO"
        assert lines[0].timestamp == datetime(2025, 11, 20, 17, 45, 32)

    def test_iter_log_lines_from_gz_file(self, sample_log_file_gz):
        """Test iterating log lines from a gzipped file"""
        lines = list(iter_log_lines(str(sample_log_file_gz), DEFAULT_DATE_FORMAT))

        assert len(lines) == 6
        assert lines[0].level == "INFO"

    def test_iter_log_lines_from_directory(self, sample_log_dir):
        """Test iterating log lines from a directory"""
        lines = list(iter_log_lines(str(sample_log_dir), DEFAULT_DATE_FORMAT))

        # Should have lines from app1.log (3), app2.log (3), and archived/old.log (1)
        assert len(lines) == 7

    def test_iter_log_lines_empty_file(self, empty_log_file):
        """Test iterating log lines from an empty file"""
        lines = list(iter_log_lines(str(empty_log_file), DEFAULT_DATE_FORMAT))

        assert len(lines) == 0

    def test_iter_log_lines_custom_date_format(
        self, tmp_path, log_lines_with_custom_format, custom_date_format
    ):
        """Test iterating log lines with custom date format"""
        log_file = tmp_path / "custom.log"
        log_file.write_text("\n".join(log_lines_with_custom_format))

        lines = list(iter_log_lines(str(log_file), custom_date_format))

        assert len(lines) == 3
        assert lines[0].timestamp == datetime(2025, 11, 20, 17, 45, 32)

    def test_iter_log_lines_nonexistent_file(self):
        """Test iterating log lines from a nonexistent file raises error"""
        with pytest.raises(FileNotFoundError):
            list(iter_log_lines("/nonexistent/path.log", DEFAULT_DATE_FORMAT))
