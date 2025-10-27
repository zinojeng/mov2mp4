"""Progress tracking for video conversions."""

import re
import logging
from typing import Optional
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Track and display conversion progress using tqdm."""

    def __init__(self, total_files: int = 1, verbose: bool = False):
        """
        Initialize the progress tracker.

        Args:
            total_files: Total number of files to convert
            verbose: Enable verbose output
        """
        self.total_files = total_files
        self.verbose = verbose
        self.current_file = 0
        self.current_pbar: Optional[tqdm] = None
        self.overall_pbar: Optional[tqdm] = None
        self.duration: Optional[float] = None

        # Create overall progress bar if multiple files
        if total_files > 1:
            self.overall_pbar = tqdm(
                total=total_files,
                desc="Overall Progress",
                unit="file",
                position=0,
                leave=True
            )

    def start_file(self, filename: str, duration: Optional[float] = None) -> None:
        """
        Start tracking progress for a new file.

        Args:
            filename: Name of the file being converted
            duration: Duration of the video in seconds (if known)
        """
        self.current_file += 1
        self.duration = duration

        # Close previous progress bar if exists
        if self.current_pbar:
            self.current_pbar.close()

        # Create progress bar for current file
        desc = f"Converting {filename}"
        if self.total_files > 1:
            desc = f"[{self.current_file}/{self.total_files}] {desc}"

        position = 1 if self.overall_pbar else 0

        if duration:
            # Use duration as total if known
            self.current_pbar = tqdm(
                total=duration,
                desc=desc,
                unit="s",
                position=position,
                leave=False
            )
        else:
            # Use indeterminate progress
            self.current_pbar = tqdm(
                desc=desc,
                unit="frames",
                position=position,
                leave=False
            )

    def update(self, line: str) -> None:
        """
        Update progress based on FFmpeg output line.

        Args:
            line: Line of output from FFmpeg
        """
        if not self.current_pbar:
            return

        if self.verbose:
            logger.debug(f"FFmpeg: {line.strip()}")

        # Parse FFmpeg progress output
        # Look for time=HH:MM:SS.MS or time=SS.MS
        time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
        if time_match:
            hours, minutes, seconds = time_match.groups()
            current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

            if self.duration:
                # Update to absolute position
                self.current_pbar.n = current_time
                self.current_pbar.refresh()
            else:
                # Update by increment
                if hasattr(self.current_pbar, 'last_time'):
                    increment = current_time - self.current_pbar.last_time
                    self.current_pbar.update(increment)
                self.current_pbar.last_time = current_time
            return

        # Alternative: look for frame count
        frame_match = re.search(r'frame=\s*(\d+)', line)
        if frame_match and not self.duration:
            frames = int(frame_match.group(1))
            if not hasattr(self.current_pbar, 'last_frame'):
                self.current_pbar.last_frame = 0
            increment = frames - self.current_pbar.last_frame
            if increment > 0:
                self.current_pbar.update(increment)
                self.current_pbar.last_frame = frames

    def finish_file(self, success: bool = True) -> None:
        """
        Mark the current file as complete.

        Args:
            success: Whether the conversion was successful
        """
        if self.current_pbar:
            if success and self.duration:
                self.current_pbar.n = self.duration
            self.current_pbar.close()
            self.current_pbar = None

        if self.overall_pbar:
            self.overall_pbar.update(1)

    def finish(self) -> None:
        """Clean up all progress bars."""
        if self.current_pbar:
            self.current_pbar.close()
            self.current_pbar = None

        if self.overall_pbar:
            self.overall_pbar.close()
            self.overall_pbar = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.finish()
