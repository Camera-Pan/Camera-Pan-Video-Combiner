#!/usr/bin/env python3
"""
Setup script for compiling Camera-Pan Video Combiner to Windows executable using py2exe.

Usage:
    python setup.py py2exe

This will create a 'dist' folder containing the executable and all dependencies.
"""

from distutils.core import setup
import py2exe
import sys
import os

# Include additional data files and dependencies
data_files = [
    # Include the FFmpeg binaries
    ("ffmpeg/bin", [
        "ffmpeg/bin/ffmpeg.exe"
    ]),
    # Include FFmpeg documentation
    ("ffmpeg", ["ffmpeg/LICENSE.txt"])
]

# Include Microsoft Visual C++ runtime if needed
sys.path.append("C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Redist\\MSVC\\v143\\x64\\Microsoft.VC143.CRT")

setup(
    name="Camera-Pan Video Combiner",
    version="2.0.0",
    description="Video merging tool for panoramic camera recordings with direct FFmpeg integration",
    author="Camera Pan Video Combiner Tool",
    
    # Main application
    windows=[{
        "script": "main.py",
        "icon_resources": [(1, "favicon.ico")],  # Use favicon.ico as the executable icon
        "dest_base": "CameraPanVideoCombiner"
    }],
    
    # Options for py2exe
    options={
        "py2exe": {
            "bundle_files": 1,  # Bundle everything into a single executable
            "compressed": True,  # Compress the library archive
            "optimize": 2,       # Optimize bytecode
            "dist_dir": "dist",  # Output directory
            "includes": [
                "tkinter",
                "tkinter.filedialog", 
                "tkinter.messagebox",
                "tkinter.ttk",
                "os",
                "re", 
                "datetime",
                "threading",
                "glob",
                "sys",
                "subprocess",
                "pathlib",
                "tempfile"
            ],
            "excludes": [
                "test",
                "unittest",
                "pdb",
                "doctest",
                "difflib",
                "ffmpeg"  # Exclude ffmpeg-python since we're not using it anymore
            ],
        }
    },
    
    # Data files to include
    data_files=data_files,
    
    # Require Python 3.6+
    python_requires=">=3.6",
    
    # Zip file options
    zipfile=None,  # Include everything in the executable
) 