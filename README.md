# MOV to MP4 Converter

A command-line tool to convert MOV video files to MP4 format using FFmpeg, with support for batch processing, quality presets, and parallel conversions.

## Features

- Convert single or multiple MOV files to MP4
- Three quality presets (low, medium, high)
- Batch processing with recursive directory support
- Real-time progress tracking with progress bars
- Parallel conversion support for faster batch processing
- Cross-platform (macOS, Linux, Windows)
- Preserves video quality with configurable compression
- Comprehensive error handling and validation

## Requirements

- Python 3.8 or higher
- FFmpeg installed on your system

## Installation

### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install ffmpeg
```

**Windows:**
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) and add to your PATH.

### Install mov2mp4

```bash
# Clone or download this repository
cd mov2mp4

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Usage

### Basic Usage

Convert a single MOV file:
```bash
mov2mp4 video.mov
```

Convert multiple files:
```bash
mov2mp4 video1.mov video2.mov video3.mov
```

Convert all MOV files in a directory:
```bash
mov2mp4 /path/to/videos/
```

### Options

```
-o, --output PATH       Output directory (default: same as input)
-q, --quality LEVEL     Quality level: low/medium/high (default: medium)
-r, --recursive         Process directories recursively
-p, --parallel N        Number of parallel conversions (default: 1)
-v, --verbose           Enable verbose output
--help                  Show help message
--version               Show version
```

### Examples

Convert with high quality to specific directory:
```bash
mov2mp4 input.mov -q high -o /path/to/output/
```

Convert all MOV files recursively with 4 parallel conversions:
```bash
mov2mp4 /path/to/videos/ -r -p 4
```

Convert with verbose output:
```bash
mov2mp4 video.mov -v
```

## Quality Presets

| Quality | CRF | Preset | Description |
|---------|-----|--------|-------------|
| Low     | 28  | fast   | Smaller file size, lower quality |
| Medium  | 23  | medium | Balanced (default) |
| High    | 18  | slow   | Best quality, larger file size |

CRF (Constant Rate Factor) ranges from 0 (lossless) to 51 (worst quality). Lower values mean better quality.

## Output Format

The converter uses the following FFmpeg settings:
- Video codec: H.264 (libx264)
- Audio codec: AAC
- Audio bitrate: 128k
- Optimized for streaming (faststart)

## Development

### Project Structure
```
mov2mp4/
├── mov2mp4/
│   ├── __init__.py
│   ├── cli.py           # Command-line interface
│   ├── converter.py     # Core conversion logic
│   ├── validator.py     # File validation
│   ├── progress.py      # Progress tracking
│   └── utils.py         # Helper functions
├── tests/
│   └── ...
├── setup.py
├── requirements.txt
├── README.md
└── .speckit.*          # Spec Kit documentation
```

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
```

## Spec-Driven Development

This project was built using [Spec Kit](https://github.com/github/spec-kit), following the Spec-Driven Development methodology. The specification files are included:

- `.speckit.constitution` - Project principles and standards
- `.speckit.specification` - Feature specifications
- `.speckit.plan` - Technical implementation plan
- `.speckit.tasks` - Task breakdown

## Troubleshooting

### FFmpeg not found
Make sure FFmpeg is installed and accessible from your PATH:
```bash
ffmpeg -version
```

### Permission denied
Ensure you have write permissions in the output directory.

### Out of memory
Try processing fewer files in parallel or convert files sequentially:
```bash
mov2mp4 /path/to/videos/ -p 1
```

### Corrupted output
Check the input file is valid:
```bash
ffmpeg -v error -i input.mov -f null -
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [FFmpeg](https://ffmpeg.org/)
- CLI powered by [Click](https://click.palletsprojects.com/)
- Progress bars by [tqdm](https://github.com/tqdm/tqdm)
