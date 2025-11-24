"""
Tests for LogFilters class and build_filters function
"""

import re
from datetime import datetime

import pytest

from cli import LogFilters, LogLine, build_filters, DEFAULT_DATE_FORMAT


class TestLogFilters:
    """Tests for LogFilters class"""
    
    def test_filters_no_filters(self):
        """Test filters with no conditions pass all lines"""
        filters = LogFilters()
        line = LogLine("test.log", "Any log line", datetime.now(), "INFO")
        
        assert filters.keep(line) is True
    
    def test_filters_from_timestamp(self):
        """Test filtering by from_ts (lower bound)"""
        from_ts = datetime(2025, 11, 20, 17, 45, 30)
        filters = LogFilters(from_ts=from_ts)
        
        line_before = LogLine("test.log", "Before", datetime(2025, 11, 20, 17, 45, 29), "INFO")
        line_equal = LogLine("test.log", "Equal", datetime(2025, 11, 20, 17, 45, 30), "INFO")
        line_after = LogLine("test.log", "After", datetime(2025, 11, 20, 17, 45, 31), "INFO")
        
        assert filters.keep(line_before) is False
        assert filters.keep(line_equal) is True
        assert filters.keep(line_after) is True
    
    def test_filters_to_timestamp(self):
        """Test filtering by to_ts (upper bound)"""
        to_ts = datetime(2025, 11, 20, 17, 45, 30)
        filters = LogFilters(to_ts=to_ts)
        
        line_before = LogLine("test.log", "Before", datetime(2025, 11, 20, 17, 45, 29), "INFO")
        line_equal = LogLine("test.log", "Equal", datetime(2025, 11, 20, 17, 45, 30), "INFO")
        line_after = LogLine("test.log", "After", datetime(2025, 11, 20, 17, 45, 31), "INFO")
        
        assert filters.keep(line_before) is True
        assert filters.keep(line_equal) is True
        assert filters.keep(line_after) is False
    
    def test_filters_timestamp_range(self):
        """Test filtering by timestamp range"""
        from_ts = datetime(2025, 11, 20, 17, 45, 30)
        to_ts = datetime(2025, 11, 20, 17, 45, 35)
        filters = LogFilters(from_ts=from_ts, to_ts=to_ts)
        
        line_before = LogLine("test.log", "Before", datetime(2025, 11, 20, 17, 45, 29), "INFO")
        line_inside = LogLine("test.log", "Inside", datetime(2025, 11, 20, 17, 45, 32), "INFO")
        line_after = LogLine("test.log", "After", datetime(2025, 11, 20, 17, 45, 36), "INFO")
        
        assert filters.keep(line_before) is False
        assert filters.keep(line_inside) is True
        assert filters.keep(line_after) is False
    
    def test_filters_timestamp_no_timestamp_in_line(self):
        """Test that lines without timestamps are rejected when timestamp filter is set"""
        from_ts = datetime(2025, 11, 20, 17, 45, 30)
        filters = LogFilters(from_ts=from_ts)
        
        line_no_ts = LogLine("test.log", "No timestamp", None, "INFO")
        
        assert filters.keep(line_no_ts) is False
    
    def test_filters_single_level(self):
        """Test filtering by a single level"""
        filters = LogFilters(levels=["ERROR"])
        
        line_error = LogLine("test.log", "Error message", None, "ERROR")
        line_info = LogLine("test.log", "Info message", None, "INFO")
        
        assert filters.keep(line_error) is True
        assert filters.keep(line_info) is False
    
    def test_filters_multiple_levels(self):
        """Test filtering by multiple levels"""
        filters = LogFilters(levels=["ERROR", "WARN"])
        
        line_error = LogLine("test.log", "Error message", None, "ERROR")
        line_warn = LogLine("test.log", "Warning message", None, "WARN")
        line_info = LogLine("test.log", "Info message", None, "INFO")
        
        assert filters.keep(line_error) is True
        assert filters.keep(line_warn) is True
        assert filters.keep(line_info) is False
    
    def test_filters_level_case_insensitive(self):
        """Test that level filtering is case-insensitive"""
        filters = LogFilters(levels=["error"])
        
        line_error_upper = LogLine("test.log", "Error message", None, "ERROR")
        line_error_lower = LogLine("test.log", "Error message", None, "error")
        
        assert filters.keep(line_error_upper) is True
        assert filters.keep(line_error_lower) is True
    
    def test_filters_level_no_level_in_line(self):
        """Test that lines without levels are rejected when level filter is set"""
        filters = LogFilters(levels=["ERROR"])
        
        line_no_level = LogLine("test.log", "No level", None, None)
        
        assert filters.keep(line_no_level) is False
    
    def test_filters_substring_match(self):
        """Test filtering by substring match"""
        filters = LogFilters(match="database")
        
        line_match = LogLine("test.log", "Failed to connect to database", None, None)
        line_no_match = LogLine("test.log", "Application started", None, None)
        
        assert filters.keep(line_match) is True
        assert filters.keep(line_no_match) is False
    
    def test_filters_substring_match_case_sensitive(self):
        """Test that substring match is case-sensitive"""
        filters = LogFilters(match="Database")
        
        line_match = LogLine("test.log", "Failed to connect to Database", None, None)
        line_no_match = LogLine("test.log", "Failed to connect to database", None, None)
        
        assert filters.keep(line_match) is True
        assert filters.keep(line_no_match) is False
    
    def test_filters_regex_match(self):
        """Test filtering by regex"""
        pattern = re.compile(r"error \d+")
        filters = LogFilters(regex=pattern)
        
        line_match = LogLine("test.log", "Received error 404", None, None)
        line_no_match = LogLine("test.log", "No error code here", None, None)
        
        assert filters.keep(line_match) is True
        assert filters.keep(line_no_match) is False
    
    def test_filters_combined_all_pass(self):
        """Test combining multiple filters where line passes all"""
        from_ts = datetime(2025, 11, 20, 17, 45, 30)
        to_ts = datetime(2025, 11, 20, 17, 45, 35)
        filters = LogFilters(
            from_ts=from_ts,
            to_ts=to_ts,
            levels=["ERROR"],
            match="database"
        )
        
        line = LogLine(
            "test.log",
            "ERROR: Failed to connect to database",
            datetime(2025, 11, 20, 17, 45, 32),
            "ERROR"
        )
        
        assert filters.keep(line) is True
    
    def test_filters_combined_one_fails(self):
        """Test combining multiple filters where line fails one"""
        from_ts = datetime(2025, 11, 20, 17, 45, 30)
        to_ts = datetime(2025, 11, 20, 17, 45, 35)
        filters = LogFilters(
            from_ts=from_ts,
            to_ts=to_ts,
            levels=["ERROR"],
            match="database"
        )
        
        # Line has wrong level
        line = LogLine(
            "test.log",
            "INFO: Failed to connect to database",
            datetime(2025, 11, 20, 17, 45, 32),
            "INFO"
        )
        
        assert filters.keep(line) is False


class TestBuildFilters:
    """Tests for build_filters function"""
    
    def test_build_filters_no_filters(self):
        """Test building filters with no parameters"""
        filters = build_filters(None, None, DEFAULT_DATE_FORMAT, [], None, None)
        
        assert filters.from_ts is None
        assert filters.to_ts is None
        assert filters.levels is None
        assert filters.match is None
        assert filters.regex is None
    
    def test_build_filters_from_timestamp(self):
        """Test building filters with from_ts"""
        filters = build_filters(
            "2025-11-20 17:45:30",
            None,
            DEFAULT_DATE_FORMAT,
            [],
            None,
            None
        )
        
        assert filters.from_ts == datetime(2025, 11, 20, 17, 45, 30)
    
    def test_build_filters_to_timestamp(self):
        """Test building filters with to_ts"""
        filters = build_filters(
            None,
            "2025-11-20 17:45:30",
            DEFAULT_DATE_FORMAT,
            [],
            None,
            None
        )
        
        assert filters.to_ts == datetime(2025, 11, 20, 17, 45, 30)
    
    def test_build_filters_levels(self):
        """Test building filters with levels"""
        filters = build_filters(
            None,
            None,
            DEFAULT_DATE_FORMAT,
            ["ERROR", "WARN"],
            None,
            None
        )
        
        assert filters.levels == ["ERROR", "WARN"]
    
    def test_build_filters_match(self):
        """Test building filters with match"""
        filters = build_filters(
            None,
            None,
            DEFAULT_DATE_FORMAT,
            [],
            "database",
            None
        )
        
        assert filters.match == "database"
    
    def test_build_filters_regex(self):
        """Test building filters with regex"""
        filters = build_filters(
            None,
            None,
            DEFAULT_DATE_FORMAT,
            [],
            None,
            r"error \d+"
        )
        
        assert filters.regex is not None
        assert filters.regex.pattern == r"error \d+"
    
    def test_build_filters_invalid_date_format(self):
        """Test building filters with invalid date format raises error"""
        with pytest.raises(ValueError):
            build_filters(
                "invalid-date",
                None,
                DEFAULT_DATE_FORMAT,
                [],
                None,
                None
            )
    
    def test_build_filters_invalid_regex(self):
        """Test building filters with invalid regex raises error"""
        with pytest.raises(re.error):
            build_filters(
                None,
                None,
                DEFAULT_DATE_FORMAT,
                [],
                None,
                r"[invalid("
            )

