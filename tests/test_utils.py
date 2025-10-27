"""Tests for utility functions."""

import pytest
from mov2mp4.utils import format_time, format_size, get_quality_params


def test_format_time_seconds():
    """Test formatting time in seconds."""
    assert format_time(30) == "30s"
    assert format_time(59) == "59s"


def test_format_time_minutes():
    """Test formatting time in minutes."""
    assert format_time(60) == "1m 0s"
    assert format_time(90) == "1m 30s"
    assert format_time(125) == "2m 5s"


def test_format_time_hours():
    """Test formatting time in hours."""
    assert format_time(3600) == "1h 0m 0s"
    assert format_time(3661) == "1h 1m 1s"
    assert format_time(7325) == "2h 2m 5s"


def test_format_size_bytes():
    """Test formatting size in bytes."""
    assert format_size(100) == "100.00 B"
    assert format_size(1000) == "1000.00 B"


def test_format_size_kilobytes():
    """Test formatting size in kilobytes."""
    assert format_size(1024) == "1.00 KB"
    assert format_size(1536) == "1.50 KB"


def test_format_size_megabytes():
    """Test formatting size in megabytes."""
    assert format_size(1024 * 1024) == "1.00 MB"
    assert format_size(1024 * 1024 * 2.5) == "2.50 MB"


def test_format_size_gigabytes():
    """Test formatting size in gigabytes."""
    assert format_size(1024 * 1024 * 1024) == "1.00 GB"
    assert format_size(1024 * 1024 * 1024 * 1.5) == "1.50 GB"


def test_get_quality_params_low():
    """Test getting quality parameters for low quality."""
    params = get_quality_params('low')
    assert params['crf'] == 28
    assert params['preset'] == 'fast'


def test_get_quality_params_medium():
    """Test getting quality parameters for medium quality."""
    params = get_quality_params('medium')
    assert params['crf'] == 23
    assert params['preset'] == 'medium'


def test_get_quality_params_high():
    """Test getting quality parameters for high quality."""
    params = get_quality_params('high')
    assert params['crf'] == 18
    assert params['preset'] == 'slow'


def test_get_quality_params_default():
    """Test getting quality parameters with invalid input defaults to medium."""
    params = get_quality_params('invalid')
    assert params['crf'] == 23
    assert params['preset'] == 'medium'


def test_get_quality_params_case_insensitive():
    """Test that quality parameter lookup is case insensitive."""
    params1 = get_quality_params('HIGH')
    params2 = get_quality_params('high')
    assert params1 == params2
