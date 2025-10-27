"""Core video conversion functionality."""

import subprocess
import logging
import json
from pathlib import Path
from typing import Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .utils import get_quality_params, format_size
from .validator import (
    validate_input_file,
    validate_output_dir,
    check_disk_space,
    is_valid_video
)
from .progress import ProgressTracker

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Exception raised when video conversion fails."""
    pass


class VideoConverter:
    """Handle video conversion from MOV to MP4."""

    def __init__(self, quality: str = 'medium', verbose: bool = False):
        """
        Initialize the video converter.

        Args:
            quality: Quality level ('low', 'medium', or 'high')
            verbose: Enable verbose logging
        """
        self.quality = quality
        self.verbose = verbose
        self.quality_params = get_quality_params(quality)

    def _get_video_duration(self, input_path: Path) -> Optional[float]:
        """
        Get the duration of the video in seconds.

        Args:
            input_path: Path to the video file

        Returns:
            Duration in seconds, or None if unable to determine
        """
        try:
            result = subprocess.run(
                [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'json',
                    str(input_path)
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data.get('format', {}).get('duration', 0))
                return duration if duration > 0 else None
        except Exception as e:
            logger.warning(f"Could not get video duration: {str(e)}")

        return None

    def convert_single(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        progress_tracker: Optional[ProgressTracker] = None
    ) -> Tuple[bool, str]:
        """
        Convert a single MOV file to MP4.

        Args:
            input_path: Path to the input MOV file
            output_path: Path for the output MP4 file (optional)
            progress_tracker: Progress tracker instance (optional)

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validate input file
        valid, msg = validate_input_file(input_path)
        if not valid:
            return False, msg

        # Validate video file
        valid, msg = is_valid_video(input_path)
        if not valid:
            return False, msg

        # Determine output path
        if output_path is None:
            output_path = input_path.with_suffix('.mp4')
        elif output_path.is_dir():
            output_path = output_path / input_path.with_suffix('.mp4').name

        # Validate output directory
        valid, msg = validate_output_dir(output_path.parent)
        if not valid:
            return False, msg

        # Check disk space (estimate: same size as input)
        input_size = input_path.stat().st_size
        valid, msg = check_disk_space(output_path, input_size)
        if not valid:
            logger.warning(msg)

        # Get video duration for progress tracking
        duration = self._get_video_duration(input_path)

        # Start progress tracking
        if progress_tracker:
            progress_tracker.start_file(input_path.name, duration)

        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-crf', str(self.quality_params['crf']),
            '-preset', self.quality_params['preset'],
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',  # Optimize for streaming
            '-y',  # Overwrite output file if exists
        ]

        # Add progress output if tracker exists
        if progress_tracker:
            cmd.extend(['-progress', 'pipe:1'])

        # Add stats options for verbose mode
        if self.verbose:
            cmd.extend(['-stats'])
        else:
            cmd.extend(['-stats_period', '0.5'])

        cmd.append(str(output_path))

        logger.info(f"Converting {input_path.name} to {output_path.name}")
        logger.debug(f"Command: {' '.join(cmd)}")

        try:
            # Run FFmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Read output line by line
            for line in process.stdout:
                if progress_tracker:
                    progress_tracker.update(line)
                elif self.verbose:
                    print(line.strip())

            # Wait for process to complete
            return_code = process.wait()

            if return_code != 0:
                if progress_tracker:
                    progress_tracker.finish_file(success=False)
                return False, f"FFmpeg failed with return code {return_code}"

            # Verify output file exists and has content
            if not output_path.exists() or output_path.stat().st_size == 0:
                if progress_tracker:
                    progress_tracker.finish_file(success=False)
                return False, "Output file was not created or is empty"

            if progress_tracker:
                progress_tracker.finish_file(success=True)

            output_size = output_path.stat().st_size
            logger.info(
                f"Successfully converted {input_path.name} "
                f"({format_size(input_size)} → {format_size(output_size)})"
            )

            return True, str(output_path)

        except KeyboardInterrupt:
            logger.info("Conversion interrupted by user")
            # Clean up partial output file
            if output_path.exists():
                output_path.unlink()
            if progress_tracker:
                progress_tracker.finish_file(success=False)
            raise
        except Exception as e:
            logger.error(f"Conversion error: {str(e)}")
            # Clean up partial output file
            if output_path.exists():
                output_path.unlink()
            if progress_tracker:
                progress_tracker.finish_file(success=False)
            return False, f"Conversion error: {str(e)}"

    def convert_batch(
        self,
        input_files: List[Path],
        output_dir: Optional[Path] = None,
        parallel: int = 1
    ) -> List[Tuple[Path, bool, str]]:
        """
        Convert multiple MOV files to MP4.

        Args:
            input_files: List of input MOV file paths
            output_dir: Output directory (optional, defaults to same as input)
            parallel: Number of parallel conversions (default: 1)

        Returns:
            List of tuples (input_path, success, message)
        """
        results = []

        with ProgressTracker(total_files=len(input_files), verbose=self.verbose) as tracker:
            if parallel <= 1:
                # Sequential processing
                for input_path in input_files:
                    output_path = output_dir if output_dir else input_path.parent
                    success, msg = self.convert_single(input_path, output_path, tracker)
                    results.append((input_path, success, msg))
            else:
                # Parallel processing
                with ThreadPoolExecutor(max_workers=parallel) as executor:
                    # Submit all tasks
                    future_to_file = {
                        executor.submit(
                            self.convert_single,
                            input_path,
                            output_dir if output_dir else input_path.parent,
                            None  # No progress tracker for parallel mode
                        ): input_path
                        for input_path in input_files
                    }

                    # Collect results as they complete
                    for future in as_completed(future_to_file):
                        input_path = future_to_file[future]
                        try:
                            success, msg = future.result()
                            results.append((input_path, success, msg))
                            tracker.finish_file(success)
                        except Exception as e:
                            logger.error(f"Error processing {input_path.name}: {str(e)}")
                            results.append((input_path, False, str(e)))
                            tracker.finish_file(success=False)

        return results
