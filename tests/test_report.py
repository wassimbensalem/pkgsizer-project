"""Tests for report module."""

from pkgsizer.report import format_size, parse_size_threshold


def test_format_size():
    """Test size formatting."""
    assert format_size(0) == "0.00 B"
    assert format_size(512) == "512.00 B"
    assert format_size(1024) == "1.00 KB"
    assert format_size(1024 * 1024) == "1.00 MB"
    assert format_size(1024 * 1024 * 1024) == "1.00 GB"
    assert format_size(1536) == "1.50 KB"


def test_parse_size_threshold():
    """Test parsing size thresholds."""
    assert parse_size_threshold("1024") == 1024
    assert parse_size_threshold("1KB") == 1024
    assert parse_size_threshold("1MB") == 1024 * 1024
    assert parse_size_threshold("1GB") == 1024 * 1024 * 1024
    assert parse_size_threshold("1.5GB") == int(1.5 * 1024 * 1024 * 1024)
    assert parse_size_threshold("100B") == 100

