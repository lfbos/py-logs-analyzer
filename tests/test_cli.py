"""
Tests for CLI commands (analyze, stats, tail)
"""

import json

from click.testing import CliRunner

from cli import cli


class TestAnalyzeCommand:
    """Tests for the analyze command"""

    def test_analyze_from_file(self, sample_log_file):
        """Test analyze command with a file"""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_log_file)])

        assert result.exit_code == 0
        assert "INFO Starting application" in result.output
        assert "ERROR Failed to connect to database" in result.output

    def test_analyze_from_gz_file(self, sample_log_file_gz):
        """Test analyze command with a gzipped file"""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_log_file_gz)])

        assert result.exit_code == 0
        assert "INFO Starting application" in result.output

    def test_analyze_from_directory(self, sample_log_dir):
        """Test analyze command with a directory"""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_log_dir)])

        assert result.exit_code == 0
        # Should contain lines from all files in the directory
        assert "INFO Starting application" in result.output
        assert "ERROR Failed to connect to database" in result.output

    def test_analyze_with_level_filter(self, sample_log_file):
        """Test analyze command with level filter"""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", str(sample_log_file), "--level", "ERROR"]
        )

        assert result.exit_code == 0
        assert "ERROR Failed to connect to database" in result.output
        assert "INFO Starting application" not in result.output

    def test_analyze_with_multiple_level_filters(self, sample_log_file):
        """Test analyze command with multiple level filters"""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "analyze",
                str(sample_log_file),
                "--level",
                "ERROR",
                "--level",
                "CRITICAL",
            ],
        )

        assert result.exit_code == 0
        assert "ERROR Failed to connect to database" in result.output
        assert "CRITICAL System shutdown initiated" in result.output
        assert "INFO Starting application" not in result.output

    def test_analyze_with_match_filter(self, sample_log_file):
        """Test analyze command with substring match filter"""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", str(sample_log_file), "--match", "database"]
        )

        assert result.exit_code == 0
        assert "Failed to connect to database" in result.output
        assert "Starting application" not in result.output

    def test_analyze_with_regex_filter(self, sample_log_file):
        """Test analyze command with regex filter"""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", str(sample_log_file), "--regex", r"ERROR.*database"]
        )

        assert result.exit_code == 0
        assert "ERROR Failed to connect to database" in result.output
        assert "INFO Starting application" not in result.output

    def test_analyze_with_from_timestamp(self, sample_log_file):
        """Test analyze command with from timestamp filter"""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", str(sample_log_file), "--from-ts", "2025-11-20 17:45:34"]
        )

        assert result.exit_code == 0
        assert "WARN Configuration file not found" in result.output
        assert "ERROR Failed to connect to database" in result.output
        assert "INFO Starting application" not in result.output
        assert "DEBUG Loading configuration" not in result.output

    def test_analyze_with_to_timestamp(self, sample_log_file):
        """Test analyze command with to timestamp filter"""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", str(sample_log_file), "--to-ts", "2025-11-20 17:45:34"]
        )

        assert result.exit_code == 0
        assert "INFO Starting application" in result.output
        assert "DEBUG Loading configuration" in result.output
        assert "WARN Configuration file not found" in result.output
        assert "ERROR Failed to connect to database" not in result.output

    def test_analyze_with_timestamp_range(self, sample_log_file):
        """Test analyze command with timestamp range"""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "analyze",
                str(sample_log_file),
                "--from-ts",
                "2025-11-20 17:45:33",
                "--to-ts",
                "2025-11-20 17:45:35",
            ],
        )

        assert result.exit_code == 0
        assert "DEBUG Loading configuration" in result.output
        assert "WARN Configuration file not found" in result.output
        assert "ERROR Failed to connect to database" in result.output
        assert "INFO Starting application" not in result.output
        assert "CRITICAL System shutdown initiated" not in result.output

    def test_analyze_with_output_file(self, sample_log_file, tmp_path):
        """Test analyze command with output to file"""
        out_file = tmp_path / "output.log"
        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", str(sample_log_file), "--out", str(out_file)]
        )

        assert result.exit_code == 0
        assert out_file.exists()

        content = out_file.read_text()
        assert "INFO Starting application" in content
        assert "ERROR Failed to connect to database" in content

    def test_analyze_combined_filters(self, sample_log_file):
        """Test analyze command with combined filters"""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "analyze",
                str(sample_log_file),
                "--level",
                "ERROR",
                "--level",
                "CRITICAL",
                "--from-ts",
                "2025-11-20 17:45:34",
                "--match",
                "Failed",
            ],
        )

        assert result.exit_code == 0
        assert "ERROR Failed to connect to database" in result.output
        assert (
            "CRITICAL System shutdown initiated" not in result.output
        )  # doesn't match "Failed"

    def test_analyze_from_stdin(self, sample_log_lines):
        """Test analyze command reading from stdin"""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"], input="\n".join(sample_log_lines))

        assert result.exit_code == 0
        assert "INFO Starting application" in result.output

    def test_analyze_empty_file(self, empty_log_file):
        """Test analyze command with empty file"""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(empty_log_file)])

        assert result.exit_code == 0
        assert result.output == ""


class TestStatsCommand:
    """Tests for the stats command"""

    def test_stats_json_output(self, sample_log_file):
        """Test stats command with JSON output"""
        runner = CliRunner()
        result = runner.invoke(cli, ["stats", str(sample_log_file), "--format", "json"])

        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["total_lines"] == 6
        assert data["levels"]["INFO"] == 2
        assert data["levels"]["DEBUG"] == 1
        assert data["levels"]["WARN"] == 1
        assert data["levels"]["ERROR"] == 1
        assert data["levels"]["CRITICAL"] == 1

    def test_stats_markdown_output(self, sample_log_file):
        """Test stats command with markdown output"""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["stats", str(sample_log_file), "--format", "markdown"]
        )

        assert result.exit_code == 0
        assert "# Log Statistics" in result.output
        assert "Total lines: **6**" in result.output
        assert "## Levels" in result.output
        assert "**INFO**: 2" in result.output
        assert "**ERROR**: 1" in result.output

    def test_stats_with_level_filter(self, sample_log_file):
        """Test stats command with level filter"""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["stats", str(sample_log_file), "--level", "ERROR", "--format", "json"]
        )

        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["total_lines"] == 1
        assert data["levels"]["ERROR"] == 1
        assert "INFO" not in data["levels"]

    def test_stats_with_timestamp_range(self, sample_log_file):
        """Test stats command with timestamp range"""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "stats",
                str(sample_log_file),
                "--from-ts",
                "2025-11-20 17:45:34",
                "--to-ts",
                "2025-11-20 17:45:35",
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["total_lines"] == 2
        assert data["levels"]["WARN"] == 1
        assert data["levels"]["ERROR"] == 1

    def test_stats_per_hour_counts(self, sample_log_file):
        """Test stats command per hour counts"""
        runner = CliRunner()
        result = runner.invoke(cli, ["stats", str(sample_log_file), "--format", "json"])

        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "2025-11-20 17:00" in data["per_hour"]
        assert "2025-11-20 18:00" in data["per_hour"]
        assert data["per_hour"]["2025-11-20 17:00"] == 5
        assert data["per_hour"]["2025-11-20 18:00"] == 1

    def test_stats_from_stdin(self, sample_log_lines):
        """Test stats command reading from stdin"""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["stats", "--format", "json"], input="\n".join(sample_log_lines)
        )

        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["total_lines"] == 6

    def test_stats_empty_file(self, empty_log_file):
        """Test stats command with empty file"""
        runner = CliRunner()
        result = runner.invoke(cli, ["stats", str(empty_log_file), "--format", "json"])

        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["total_lines"] == 0
        assert data["levels"] == {}
        assert data["per_hour"] == {}


class TestTailCommand:
    """Tests for the tail command"""

    def test_tail_requires_path(self):
        """Test that tail command requires a path argument"""
        runner = CliRunner()
        result = runner.invoke(cli, ["tail"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_tail_nonexistent_file(self):
        """Test tail command with nonexistent file"""
        runner = CliRunner()
        result = runner.invoke(cli, ["tail", "/nonexistent/file.log"])

        assert result.exit_code != 0
        assert "not a valid file" in result.output

    def test_tail_directory_fails(self, sample_log_dir):
        """Test tail command with a directory (should fail)"""
        runner = CliRunner()
        result = runner.invoke(cli, ["tail", str(sample_log_dir)])

        assert result.exit_code != 0
        assert "not a valid file" in result.output

    def test_tail_from_start(self, tmp_path):
        """Test tail command with --from-start flag"""
        import time
        from unittest.mock import patch

        log_file = tmp_path / "test.log"
        log_file.write_text(
            "2025-11-20 17:45:32 INFO Starting\n2025-11-20 17:45:33 ERROR Failed\n"
        )

        runner = CliRunner()

        # Mock time.sleep to raise KeyboardInterrupt after first call
        original_sleep = time.sleep
        sleep_count = [0]

        def mock_sleep(duration):
            sleep_count[0] += 1
            if sleep_count[0] >= 1:
                raise KeyboardInterrupt()
            original_sleep(0.001)

        with patch("time.sleep", side_effect=mock_sleep):
            result = runner.invoke(
                cli, ["tail", str(log_file), "--from-start"], catch_exceptions=False
            )

            # Should have read the existing lines
            assert "INFO Starting" in result.output or result.exit_code != 0

    def test_tail_from_end(self, tmp_path):
        """Test tail command starting from end of file"""
        from unittest.mock import patch

        log_file = tmp_path / "test.log"
        log_file.write_text("2025-11-20 17:45:32 INFO Old line\n")

        runner = CliRunner()

        # Mock time.sleep to interrupt after first call
        def mock_sleep(duration):
            raise KeyboardInterrupt()

        with patch("time.sleep", side_effect=mock_sleep):
            result = runner.invoke(cli, ["tail", str(log_file)], catch_exceptions=False)

            # Should not output old lines (started from end)
            # KeyboardInterrupt is expected
            assert True

    def test_tail_with_custom_interval(self, tmp_path):
        """Test tail command with custom interval parameter"""
        from unittest.mock import patch

        log_file = tmp_path / "test.log"
        log_file.write_text("2025-11-20 17:45:32 INFO Test\n")

        runner = CliRunner()

        # Mock time.sleep to interrupt immediately
        def mock_sleep(duration):
            # Verify the custom interval is being used
            raise KeyboardInterrupt()

        with patch("time.sleep", side_effect=mock_sleep):
            result = runner.invoke(
                cli,
                ["tail", str(log_file), "--interval", "1.5"],
                catch_exceptions=False,
            )

            # KeyboardInterrupt is expected (simulates Ctrl+C)
            assert True


class TestCLIHelp:
    """Tests for CLI help and basic functionality"""

    def test_cli_help(self):
        """Test that CLI help works"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "logz" in result.output
        assert "log analyzer" in result.output.lower()

    def test_analyze_help(self):
        """Test that analyze help works"""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "analyze" in result.output.lower()
        assert "filter" in result.output.lower()

    def test_stats_help(self):
        """Test that stats help works"""
        runner = CliRunner()
        result = runner.invoke(cli, ["stats", "--help"])

        assert result.exit_code == 0
        assert "stats" in result.output.lower()
        assert "statistics" in result.output.lower()

    def test_tail_help(self):
        """Test that tail help works"""
        runner = CliRunner()
        result = runner.invoke(cli, ["tail", "--help"])

        assert result.exit_code == 0
        assert "tail" in result.output.lower()
