"""Utility functions for the MOV to MP4 converter."""

import logging
from typing import Optional


def format_time(seconds: float) -> str:
    """
    Convert seconds to human-readable time format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string (e.g., "1h 23m 45s" or "45s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"


def format_size(bytes_size: int) -> str:
    """
    Convert bytes to human-readable size format.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 GB", "256 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        verbose: If True, set logging level to DEBUG
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# Quality presets (CRF values and presets)
QUALITY_PRESETS = {
    'low': {'crf': 28, 'preset': 'fast'},
    'medium': {'crf': 23, 'preset': 'medium'},
    'high': {'crf': 18, 'preset': 'slow'}
}


def get_quality_params(quality: str = 'medium') -> dict:
    """
    Get FFmpeg quality parameters for the specified quality level.

    Args:
        quality: Quality level ('low', 'medium', or 'high')

    Returns:
        Dictionary with 'crf' and 'preset' keys
    """
    return QUALITY_PRESETS.get(quality.lower(), QUALITY_PRESETS['medium'])
