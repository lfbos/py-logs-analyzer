"""
Tests for LogStats class
"""

from datetime import datetime

import pytest

from cli import LogLine, LogStats


class TestLogStats:
    """Tests for LogStats class"""

    def test_stats_initialization(self):
        """Test that LogStats initializes correctly"""
        stats = LogStats()

        assert stats.total_lines == 0
        assert stats.level_counts == {}
        assert stats.per_hour_counts == {}

    def test_stats_add_single_line(self):
        """Test adding a single log line"""
        stats = LogStats()
        line = LogLine(
            "test.log",
            "2025-11-20 17:45:32 INFO Test message",
            datetime(2025, 11, 20, 17, 45, 32),
            "INFO",
        )

        stats.add(line)

        assert stats.total_lines == 1
        assert stats.level_counts["INFO"] == 1
        assert stats.per_hour_counts["2025-11-20 17:00"] == 1

    def test_stats_add_multiple_lines_same_level(self):
        """Test adding multiple lines with the same level"""
        stats = LogStats()

        for i in range(3):
            line = LogLine(
                "test.log",
                f"2025-11-20 17:45:{30 + i} INFO Test message {i}",
                datetime(2025, 11, 20, 17, 45, 30 + i),
                "INFO",
            )
            stats.add(line)

        assert stats.total_lines == 3
        assert stats.level_counts["INFO"] == 3

    def test_stats_add_multiple_levels(self):
        """Test adding lines with different levels"""
        stats = LogStats()

        lines = [
            LogLine("test.log", "INFO msg", datetime(2025, 11, 20, 17, 45, 32), "INFO"),
            LogLine(
                "test.log", "ERROR msg", datetime(2025, 11, 20, 17, 45, 33), "ERROR"
            ),
            LogLine("test.log", "WARN msg", datetime(2025, 11, 20, 17, 45, 34), "WARN"),
            LogLine("test.log", "INFO msg", datetime(2025, 11, 20, 17, 45, 35), "INFO"),
        ]

        for line in lines:
            stats.add(line)

        assert stats.total_lines == 4
        assert stats.level_counts["INFO"] == 2
        assert stats.level_counts["ERROR"] == 1
        assert stats.level_counts["WARN"] == 1

    def test_stats_add_line_without_level(self):
        """Test adding a line without a level"""
        stats = LogStats()
        line = LogLine(
            "test.log", "Test message", datetime(2025, 11, 20, 17, 45, 32), None
        )

        stats.add(line)

        assert stats.total_lines == 1
        assert stats.level_counts == {}

    def test_stats_add_line_without_timestamp(self):
        """Test adding a line without a timestamp"""
        stats = LogStats()
        line = LogLine("test.log", "INFO Test message", None, "INFO")

        stats.add(line)

        assert stats.total_lines == 1
        assert stats.level_counts["INFO"] == 1
        assert stats.per_hour_counts == {}

    def test_stats_per_hour_same_hour(self):
        """Test that lines in the same hour are grouped together"""
        stats = LogStats()

        lines = [
            LogLine("test.log", "msg 1", datetime(2025, 11, 20, 17, 15, 30), "INFO"),
            LogLine("test.log", "msg 2", datetime(2025, 11, 20, 17, 30, 45), "INFO"),
            LogLine("test.log", "msg 3", datetime(2025, 11, 20, 17, 59, 59), "INFO"),
        ]

        for line in lines:
            stats.add(line)

        assert stats.per_hour_counts["2025-11-20 17:00"] == 3

    def test_stats_per_hour_different_hours(self):
        """Test that lines in different hours are counted separately"""
        stats = LogStats()

        lines = [
            LogLine("test.log", "msg 1", datetime(2025, 11, 20, 17, 45, 30), "INFO"),
            LogLine("test.log", "msg 2", datetime(2025, 11, 20, 18, 15, 30), "INFO"),
            LogLine("test.log", "msg 3", datetime(2025, 11, 20, 19, 30, 30), "INFO"),
            LogLine("test.log", "msg 4", datetime(2025, 11, 20, 18, 45, 30), "INFO"),
        ]

        for line in lines:
            stats.add(line)

        assert stats.per_hour_counts["2025-11-20 17:00"] == 1
        assert stats.per_hour_counts["2025-11-20 18:00"] == 2
        assert stats.per_hour_counts["2025-11-20 19:00"] == 1

    def test_stats_level_case_handling(self):
        """Test that level counts handle case correctly"""
        stats = LogStats()

        lines = [
            LogLine("test.log", "msg 1", None, "info"),
            LogLine("test.log", "msg 2", None, "INFO"),
            LogLine("test.log", "msg 3", None, "Info"),
        ]

        for line in lines:
            stats.add(line)

        # All should be counted as "INFO" (uppercase)
        assert stats.level_counts["INFO"] == 3

    def test_stats_to_dict(self):
        """Test converting stats to dictionary"""
        stats = LogStats()

        lines = [
            LogLine("test.log", "INFO msg", datetime(2025, 11, 20, 17, 45, 32), "INFO"),
            LogLine(
                "test.log", "ERROR msg", datetime(2025, 11, 20, 17, 45, 33), "ERROR"
            ),
            LogLine("test.log", "INFO msg", datetime(2025, 11, 20, 18, 15, 30), "INFO"),
        ]

        for line in lines:
            stats.add(line)

        result = stats.to_dict()

        assert result["total_lines"] == 3
        assert result["levels"] == {"INFO": 2, "ERROR": 1}
        assert result["per_hour"] == {"2025-11-20 17:00": 2, "2025-11-20 18:00": 1}

    def test_stats_to_dict_empty(self):
        """Test converting empty stats to dictionary"""
        stats = LogStats()
        result = stats.to_dict()

        assert result["total_lines"] == 0
        assert result["levels"] == {}
        assert result["per_hour"] == {}

    def test_stats_comprehensive(self):
        """Test comprehensive scenario with multiple log lines"""
        stats = LogStats()

        lines = [
            LogLine(
                "test.log", "DEBUG msg", datetime(2025, 11, 20, 10, 15, 30), "DEBUG"
            ),
            LogLine("test.log", "INFO msg", datetime(2025, 11, 20, 10, 30, 30), "INFO"),
            LogLine("test.log", "INFO msg", datetime(2025, 11, 20, 11, 15, 30), "INFO"),
            LogLine("test.log", "WARN msg", datetime(2025, 11, 20, 11, 30, 30), "WARN"),
            LogLine(
                "test.log", "ERROR msg", datetime(2025, 11, 20, 12, 15, 30), "ERROR"
            ),
            LogLine(
                "test.log",
                "CRITICAL msg",
                datetime(2025, 11, 20, 12, 30, 30),
                "CRITICAL",
            ),
            LogLine("test.log", "No level", None, None),
            LogLine("test.log", "No timestamp", None, "INFO"),
        ]

        for line in lines:
            stats.add(line)

        assert stats.total_lines == 8
        assert stats.level_counts == {
            "DEBUG": 1,
            "INFO": 3,
            "WARN": 1,
            "ERROR": 1,
            "CRITICAL": 1,
        }
        assert stats.per_hour_counts == {
            "2025-11-20 10:00": 2,
            "2025-11-20 11:00": 2,
            "2025-11-20 12:00": 2,
        }
