#!/bin/bash

# MOV to MP4 Converter - Automated Start Script
# This script sets up virtual environment and runs the converter

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR="venv"
PYTHON_CMD="python3"

echo -e "${GREEN}=== MOV to MP4 Converter - Setup & Run ===${NC}\n"

# Check if Python is installed
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Found Python $PYTHON_VERSION"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  Warning: FFmpeg is not installed"
    echo "Please install FFmpeg:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Linux:   sudo apt install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1 | awk '{print $3}')
    echo -e "${GREEN}✓${NC} Found FFmpeg $FFMPEG_VERSION"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv $VENV_DIR
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip -q

# Install requirements
echo -e "\n${YELLOW}Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${RED}Error: requirements.txt not found${NC}"
    exit 1
fi

# Install the package in development mode
echo -e "\n${YELLOW}Installing mov2mp4 package...${NC}"
pip install -e . -q
echo -e "${GREEN}✓${NC} Package installed"

# Check if arguments were passed
echo -e "\n${GREEN}=== Setup Complete ===${NC}\n"

if [ $# -eq 0 ]; then
    # No arguments - show help
    echo "Usage: ./start.sh [OPTIONS] INPUT_FILES..."
    echo ""
    echo "Examples:"
    echo "  ./start.sh video.mov"
    echo "  ./start.sh video.mov -q high -o ./output/"
    echo "  ./start.sh *.mov -p 4"
    echo "  ./start.sh /path/to/videos/ -r"
    echo ""
    echo "Run with --help for full options:"
    echo "  ./start.sh --help"
    echo ""
    echo -e "${YELLOW}Virtual environment is active. You can also run directly:${NC}"
    echo "  mov2mp4 --help"
else
    # Run the converter with provided arguments
    echo -e "${GREEN}Running mov2mp4 with arguments: $@${NC}\n"
    mov2mp4 "$@"
fi

echo -e "\n${GREEN}Done!${NC}"
