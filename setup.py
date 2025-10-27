from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mov2mp4",
    version="0.1.0",
    author="Your Name",
    description="A command-line tool to convert MOV files to MP4 format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "tqdm>=4.65.0",
        "ffmpeg-python>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "mov2mp4=mov2mp4.cli:main",
        ],
    },
)
