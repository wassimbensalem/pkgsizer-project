"""Tests for size_calc module."""

import tempfile
from pathlib import Path

from pkgsizer.size_calc import calculate_path_size, should_exclude, SizeInfo


def test_calculate_file_size():
    """Test calculating size of a single file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test content")
        temp_path = Path(f.name)
    
    try:
        info = calculate_path_size(temp_path)
        assert info.size_bytes > 0
        assert info.file_count == 1
    finally:
        temp_path.unlink()


def test_calculate_directory_size():
    """Test calculating size of a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        
        # Create some files
        (temp_path / "file1.txt").write_text("content1")
        (temp_path / "file2.txt").write_text("content2")
        
        subdir = temp_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")
        
        info = calculate_path_size(temp_path)
        assert info.size_bytes > 0
        assert info.file_count == 3


def test_should_exclude():
    """Test pattern exclusion."""
    assert should_exclude(Path("__pycache__"), ["__pycache__"])
    assert should_exclude(Path("test.pyc"), ["*.pyc"])
    assert should_exclude(Path("/path/to/__pycache__/file.pyc"), ["*__pycache__*"])
    assert not should_exclude(Path("test.py"), ["*.pyc"])


def test_size_info_add():
    """Test adding SizeInfo objects."""
    info1 = SizeInfo()
    info1.size_bytes = 100
    info1.file_count = 1
    
    info2 = SizeInfo()
    info2.size_bytes = 200
    info2.file_count = 2
    
    info1.add(info2)
    assert info1.size_bytes == 300
    assert info1.file_count == 3

