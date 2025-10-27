"""Command-line interface for MOV to MP4 converter."""

import sys
import logging
from pathlib import Path
from typing import List

import click

from . import __version__
from .utils import setup_logging, format_time
from .validator import check_ffmpeg_installed
from .converter import VideoConverter

logger = logging.getLogger(__name__)


def find_mov_files(path: Path, recursive: bool = False) -> List[Path]:
    """
    Find all MOV files in the given path.

    Args:
        path: Directory path or file path
        recursive: Search recursively in subdirectories

    Returns:
        List of MOV file paths
    """
    if path.is_file():
        if path.suffix.lower() in ['.mov', '.MOV']:
            return [path]
        else:
            return []

    if path.is_dir():
        if recursive:
            pattern = '**/*.mov'
        else:
            pattern = '*.mov'

        files = list(path.glob(pattern))
        # Also find .MOV (uppercase)
        if recursive:
            files.extend(path.glob('**/*.MOV'))
        else:
            files.extend(path.glob('*.MOV'))

        return sorted(set(files))

    return []


@click.command()
@click.argument('input_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    '-o', '--output',
    type=click.Path(),
    help='Output directory for converted files (default: same as input)'
)
@click.option(
    '-q', '--quality',
    type=click.Choice(['low', 'medium', 'high'], case_sensitive=False),
    default='medium',
    help='Output quality level (default: medium)'
)
@click.option(
    '-r', '--recursive',
    is_flag=True,
    help='Process directories recursively'
)
@click.option(
    '-p', '--parallel',
    type=int,
    default=1,
    help='Number of parallel conversions (default: 1)'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose output'
)
@click.version_option(version=__version__, prog_name='mov2mp4')
def main(input_paths, output, quality, recursive, parallel, verbose):
    """
    Convert MOV video files to MP4 format.

    INPUT_PATHS can be one or more files or directories containing MOV files.

    Examples:

    \b
    # Convert a single file
    mov2mp4 video.mov

    \b
    # Convert multiple files
    mov2mp4 video1.mov video2.mov video3.mov

    \b
    # Convert all MOV files in a directory
    mov2mp4 /path/to/videos/

    \b
    # Convert with high quality to a specific output directory
    mov2mp4 input.mov -q high -o /path/to/output/

    \b
    # Convert all MOV files recursively with 4 parallel conversions
    mov2mp4 /path/to/videos/ -r -p 4
    """
    # Setup logging
    setup_logging(verbose)

    # Check FFmpeg installation
    click.echo("Checking FFmpeg installation...")
    installed, msg = check_ffmpeg_installed()
    if not installed:
        click.echo(click.style(f"Error: {msg}", fg='red'), err=True)
        click.echo("\nPlease install FFmpeg:")
        click.echo("  macOS:   brew install ffmpeg")
        click.echo("  Linux:   sudo apt install ffmpeg  (Ubuntu/Debian)")
        click.echo("           sudo yum install ffmpeg  (CentOS/RHEL)")
        click.echo("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)

    if verbose:
        click.echo(click.style(f"✓ {msg}", fg='green'))

    # Find all MOV files
    all_files = []
    for input_path in input_paths:
        path = Path(input_path)
        files = find_mov_files(path, recursive)
        all_files.extend(files)

    # Remove duplicates and sort
    all_files = sorted(set(all_files))

    if not all_files:
        click.echo(click.style("Error: No MOV files found", fg='red'), err=True)
        sys.exit(1)

    # Display summary
    click.echo(f"\nFound {len(all_files)} MOV file(s) to convert")
    click.echo(f"Quality: {quality}")
    if output:
        click.echo(f"Output directory: {output}")
    if parallel > 1:
        click.echo(f"Parallel conversions: {parallel}")
    click.echo()

    # Prepare output directory
    output_dir = Path(output) if output else None
    if output_dir and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # Create converter
    converter = VideoConverter(quality=quality, verbose=verbose)

    # Convert files
    try:
        if len(all_files) == 1:
            # Single file conversion
            input_file = all_files[0]
            from .progress import ProgressTracker

            with ProgressTracker(total_files=1, verbose=verbose) as tracker:
                success, msg = converter.convert_single(input_file, output_dir, tracker)

            if success:
                click.echo(click.style(f"\n✓ Conversion successful!", fg='green'))
                click.echo(f"Output: {msg}")
            else:
                click.echo(click.style(f"\n✗ Conversion failed: {msg}", fg='red'), err=True)
                sys.exit(1)
        else:
            # Batch conversion
            results = converter.convert_batch(all_files, output_dir, parallel)

            # Display results
            click.echo("\n" + "=" * 60)
            click.echo("CONVERSION SUMMARY")
            click.echo("=" * 60)

            successful = 0
            failed = 0

            for input_path, success, msg in results:
                if success:
                    successful += 1
                    status = click.style("✓", fg='green')
                    click.echo(f"{status} {input_path.name} → {Path(msg).name}")
                else:
                    failed += 1
                    status = click.style("✗", fg='red')
                    click.echo(f"{status} {input_path.name}: {msg}")

            click.echo("=" * 60)
            click.echo(f"Total: {len(results)} files")
            click.echo(click.style(f"Successful: {successful}", fg='green'))
            if failed > 0:
                click.echo(click.style(f"Failed: {failed}", fg='red'))
            click.echo("=" * 60)

            if failed > 0:
                sys.exit(1)

    except KeyboardInterrupt:
        click.echo(click.style("\n\nConversion interrupted by user", fg='yellow'))
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error")
        click.echo(click.style(f"\nError: {str(e)}", fg='red'), err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
