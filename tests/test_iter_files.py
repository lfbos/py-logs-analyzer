"""
Tests for iter_files function
"""

import gzip
from pathlib import Path

import pytest

from cli import iter_files


class TestIterFiles:
    """Tests for the iter_files function"""
    
    def test_iter_files_from_stdin_none(self):
        """Test iter_files with None returns stdin"""
        result = list(iter_files(None))
        
        assert len(result) == 1
        assert result[0][0] == "<stdin>"
    
    def test_iter_files_from_stdin_dash(self):
        """Test iter_files with '-' returns stdin"""
        result = list(iter_files("-"))
        
        assert len(result) == 1
        assert result[0][0] == "<stdin>"
    
    def test_iter_files_single_file(self, sample_log_file):
        """Test iter_files with a single file"""
        sources = []
        for source, file_obj in iter_files(str(sample_log_file)):
            sources.append(source)
            content = file_obj.read()
            assert "INFO Starting application" in content
        
        assert len(sources) == 1
        assert sources[0] == str(sample_log_file)
    
    def test_iter_files_single_gz_file(self, sample_log_file_gz):
        """Test iter_files with a gzipped file"""
        result = list(iter_files(str(sample_log_file_gz)))
        
        assert len(result) == 1
        source, file_obj = result[0]
        assert source == str(sample_log_file_gz)
        assert str(source).endswith(".gz")
    
    def test_iter_files_directory(self, sample_log_dir):
        """Test iter_files with a directory"""
        result = list(iter_files(str(sample_log_dir)))
        
        # Should have multiple files from the directory
        assert len(result) >= 3
        sources = [source for source, _ in result]
        assert any("app1.log" in s for s in sources)
        assert any("app2.log" in s for s in sources)
    
    def test_iter_files_directory_with_gz(self, tmp_path, sample_log_lines):
        """Test iter_files with directory containing .gz files"""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        # Create regular log file
        (log_dir / "regular.log").write_text("\n".join(sample_log_lines[:2]))
        
        # Create gzipped log file
        gz_file = log_dir / "compressed.log.gz"
        with gzip.open(gz_file, "wt", encoding="utf-8") as f:
            f.write("\n".join(sample_log_lines[2:]))
        
        result = list(iter_files(str(log_dir)))
        
        assert len(result) == 2
        sources = [source for source, _ in result]
        assert any("regular.log" in s for s in sources)
        assert any("compressed.log.gz" in s for s in sources)
    
    def test_iter_files_directory_skips_non_files(self, tmp_path):
        """Test that iter_files skips non-file entries"""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        # Create a subdirectory (should be skipped in the count but traversed)
        sub_dir = log_dir / "subdir"
        sub_dir.mkdir()
        
        # Create a file in the subdirectory
        (sub_dir / "nested.log").write_text("Nested log")
        
        result = list(iter_files(str(log_dir)))
        
        # Should only yield the file, not the directory itself
        assert len(result) == 1
        source, file_obj = result[0]
        assert "nested.log" in source
    
    def test_iter_files_empty_directory(self, tmp_path):
        """Test iter_files with an empty directory"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        result = list(iter_files(str(empty_dir)))
        
        assert len(result) == 0

