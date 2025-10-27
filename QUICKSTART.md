# Quick Start Guide

## Installation

1. **Install FFmpeg** (if not already installed):
   ```bash
   # macOS
   brew install ffmpeg

   # Linux
   sudo apt install ffmpeg
   ```

2. **Install the converter**:
   ```bash
   cd /Users/zino/Desktop/OpenAI/mov2mp4
   pip install -e .
   ```

3. **Verify installation**:
   ```bash
   mov2mp4 --version
   mov2mp4 --help
   ```

## Basic Usage

### Convert a single file
```bash
mov2mp4 video.mov
```

### Convert with options
```bash
# High quality conversion
mov2mp4 video.mov -q high

# Save to specific directory
mov2mp4 video.mov -o ./converted/

# Multiple files
mov2mp4 video1.mov video2.mov video3.mov
```

### Batch conversion
```bash
# Convert all MOV files in current directory
mov2mp4 .

# Convert all MOV files recursively
mov2mp4 /path/to/videos/ -r

# Parallel processing (4 files at once)
mov2mp4 /path/to/videos/ -p 4
```

## Testing Without Installation

You can also run directly with Python:
```bash
cd /Users/zino/Desktop/OpenAI/mov2mp4
python -m mov2mp4.cli video.mov
```

## Examples

### Example 1: Single file, medium quality (default)
```bash
mov2mp4 vacation.mov
# Output: vacation.mp4 (in the same directory)
```

### Example 2: High quality to specific directory
```bash
mov2mp4 important-video.mov -q high -o ~/Videos/converted/
# Output: ~/Videos/converted/important-video.mp4
```

### Example 3: Batch convert with progress
```bash
mov2mp4 ~/Videos/*.mov -v
# Converts all MOV files with verbose output
```

### Example 4: Fast parallel batch conversion
```bash
mov2mp4 ~/Videos/ -r -p 4 -q low
# Recursively find all MOV files
# Convert 4 files in parallel
# Use low quality for smaller file sizes
```

## Troubleshooting

### "FFmpeg not found"
Install FFmpeg using your package manager (see installation above).

### Check FFmpeg installation
```bash
ffmpeg -version
which ffmpeg
```

### Run tests
```bash
pip install pytest
pytest tests/
```

## Spec Kit Documentation

This project follows Spec-Driven Development. View the specifications:
- `.speckit.constitution` - Project principles
- `.speckit.specification` - Feature requirements
- `.speckit.plan` - Technical design
- `.speckit.tasks` - Implementation tasks
