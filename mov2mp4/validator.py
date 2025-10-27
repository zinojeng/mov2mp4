"""File validation and system checks for the MOV to MP4 converter."""

import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


def check_ffmpeg_installed() -> Tuple[bool, str]:
    """
    Check if FFmpeg is installed and accessible.

    Returns:
        Tuple of (is_installed: bool, message: str)
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Extract version from first line
            version_line = result.stdout.split('\n')[0]
            return True, f"FFmpeg found: {version_line}"
        else:
            return False, "FFmpeg command failed"
    except FileNotFoundError:
        return False, "FFmpeg not found. Please install FFmpeg first."
    except subprocess.TimeoutExpired:
        return False, "FFmpeg check timed out"
    except Exception as e:
        return False, f"Error checking FFmpeg: {str(e)}"


def validate_input_file(file_path: Path) -> Tuple[bool, str]:
    """
    Validate that the input file exists and is a MOV file.

    Args:
        file_path: Path to the input file

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    if not file_path.is_file():
        return False, f"Not a file: {file_path}"

    if file_path.suffix.lower() not in ['.mov', '.MOV']:
        return False, f"Not a MOV file: {file_path}"

    if file_path.stat().st_size == 0:
        return False, f"File is empty: {file_path}"

    return True, "Valid input file"


def validate_output_dir(dir_path: Path) -> Tuple[bool, str]:
    """
    Validate that the output directory exists and is writable.

    Args:
        dir_path: Path to the output directory

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not dir_path.exists():
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return True, f"Created output directory: {dir_path}"
        except Exception as e:
            return False, f"Cannot create directory: {str(e)}"

    if not dir_path.is_dir():
        return False, f"Not a directory: {dir_path}"

    if not os.access(dir_path, os.W_OK):
        return False, f"Directory is not writable: {dir_path}"

    return True, "Valid output directory"


def check_disk_space(output_path: Path, required_bytes: int) -> Tuple[bool, str]:
    """
    Check if there's enough disk space for the output file.

    Args:
        output_path: Path where the output file will be written
        required_bytes: Estimated space needed in bytes

    Returns:
        Tuple of (has_space: bool, message: str)
    """
    try:
        stat = shutil.disk_usage(output_path.parent)
        available = stat.free

        # Add 10% buffer
        required_with_buffer = int(required_bytes * 1.1)

        if available < required_with_buffer:
            from .utils import format_size
            return False, (
                f"Insufficient disk space. "
                f"Required: {format_size(required_with_buffer)}, "
                f"Available: {format_size(available)}"
            )

        return True, "Sufficient disk space"
    except Exception as e:
        logger.warning(f"Could not check disk space: {str(e)}")
        # Don't fail if we can't check, just warn
        return True, "Could not verify disk space"


def is_valid_video(file_path: Path) -> Tuple[bool, str]:
    """
    Use FFmpeg to verify the file is a valid video file.

    Args:
        file_path: Path to the video file

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-count_packets',
                '-show_entries', 'stream=codec_type',
                '-of', 'csv=p=0',
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return False, f"FFprobe error: {result.stderr}"

        if 'video' not in result.stdout.lower():
            return False, "File does not contain a video stream"

        return True, "Valid video file"
    except FileNotFoundError:
        logger.warning("ffprobe not found, skipping detailed validation")
        return True, "Could not verify (ffprobe not found)"
    except subprocess.TimeoutExpired:
        return False, "Video validation timed out"
    except Exception as e:
        logger.warning(f"Could not validate video: {str(e)}")
        return True, "Could not verify video"
