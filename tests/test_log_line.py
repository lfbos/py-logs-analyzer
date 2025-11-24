"""
Tests for LogLine class
"""

from datetime import datetime

import pytest

from cli import LogLine


class TestLogLine:
    """Tests for the LogLine class"""

    def test_create_log_line_basic(self):
        """Test creating a basic LogLine with required fields"""
        line = LogLine(source="test.log", raw="2025-11-20 17:45:32 INFO Test message")

        assert line.source == "test.log"
        assert line.raw == "2025-11-20 17:45:32 INFO Test message"
        assert line.timestamp is None
        assert line.level is None

    def test_create_log_line_with_timestamp(self):
        """Test creating a LogLine with timestamp"""
        ts = datetime(2025, 11, 20, 17, 45, 32)
        line = LogLine(
            source="test.log", raw="2025-11-20 17:45:32 INFO Test message", timestamp=ts
        )

        assert line.timestamp == ts

    def test_create_log_line_with_level(self):
        """Test creating a LogLine with level"""
        line = LogLine(
            source="test.log", raw="2025-11-20 17:45:32 INFO Test message", level="INFO"
        )

        assert line.level == "INFO"

    def test_create_log_line_complete(self):
        """Test creating a LogLine with all fields"""
        ts = datetime(2025, 11, 20, 17, 45, 32)
        line = LogLine(
            source="test.log",
            raw="2025-11-20 17:45:32 ERROR Database connection failed",
            timestamp=ts,
            level="ERROR",
        )

        assert line.source == "test.log"
        assert line.raw == "2025-11-20 17:45:32 ERROR Database connection failed"
        assert line.timestamp == ts
        assert line.level == "ERROR"

    def test_log_line_from_stdin(self):
        """Test creating a LogLine from stdin"""
        line = LogLine(source="<stdin>", raw="Test message from stdin")

        assert line.source == "<stdin>"
        assert line.raw == "Test message from stdin"
