# Camera-Pan Video Combiner Tool

A GUI application for merging panoramic video files from camera recordings. This tool automatically finds, sorts, and merges video files with specific naming patterns into a single panorama video, with flexible input selection options.

## Features

- **User-friendly GUI** built with tkinter with grey/blue theme
- **Flexible input selection**: Choose between folder selection or specific file selection
- **Automatic file detection** for videos starting with "RecM0"
- **Chronological sorting** based on timestamps in filenames
- **Seamless video merging** using bundled FFmpeg binary (no re-encoding for speed)
- **Real-time progress tracking** with detailed logging
- **Error handling** with user-friendly messages
- **Windows executable compilation** ready with py2exe
- **Self-contained**: Includes FFmpeg binary - no external dependencies needed

## New in Version 2.0.0

### Direct FFmpeg Integration
- **🚀 Removed ffmpeg-python dependency**: Now uses bundled FFmpeg binary directly
- **⚡ Faster processing**: Direct concatenation without re-encoding preserves quality and speed
- **📦 Self-contained**: FFmpeg binary included - no external installations required
- **🔧 More reliable**: Direct subprocess calls eliminate ffmpeg-python compatibility issues

### File Selection Mode (from v1.1.0)
- **📁 Select Folder (Recommended)**: Automatically finds all RecM0*.mp4 files in a folder
- **📄 Select Specific Files**: Manually choose specific video files with multi-file selection
- Smart filtering: Only files starting with "RecM0" are included in the merge
- Same timestamp parsing and sorting logic for both modes

## Requirements

### System Requirements
- Windows 10 or later
- Python 3.6 or higher (for running from source)
- FFmpeg binary (bundled with application)

### Python Dependencies
- `py2exe` - For Windows executable compilation (development only)
- `tkinter` - GUI framework (built-in with Python)

**No external video processing dependencies required!**

## Installation

### Option 1: Run from Source

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd Camera-Pan-Video-Combiner
   ```

2. **Install dependencies (optional - only for compilation)**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

### Option 2: Compile to Windows Executable

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Compile to executable**
   ```bash
   python setup.py py2exe
   ```

3. **Run the executable**
   The compiled executable will be in the `dist` folder:
   ```
   dist/CameraPanVideoCombiner.exe
   ```

## Usage

### Input File Format
The tool looks for video files with the following naming pattern:
```
RecM0X_YYYYMMDD_HHMMSS_...
```

**Examples:**
- `RecM05_20231215_143022_001.mp4`
- `RecM01_20231215_143045_002.mp4`
- `RecM03_20231215_143108_003.mp4`

### Step-by-Step Guide

1. **Launch the application**
   - Run `python main.py` or use the compiled executable

2. **Choose Input Selection Method**
   - **📁 Select Folder (Recommended)**: Automatically processes all valid files in a folder
   - **📄 Select Specific Files**: Manually choose individual files

3. **Select Input Source**
   - **For Folder Mode**: Click "Browse Folder" and choose the folder containing RecM0* videos
   - **For File Mode**: Click "Browse Files" and select specific RecM0* video files

4. **Select Output Folder** 
   - Click "Browse" next to "Select Output Folder"
   - Choose where you want the merged `Panorama.mp4` file to be saved

5. **Start Merging**
   - Click the "🎬 Merge Videos" button
   - Monitor progress in the log area
   - Wait for the completion message

6. **Upload to VideoArena**
   - Once complete, you'll see: "✅ Merging complete! You can now upload the video to VideoArena."
   - The merged file will be saved as `Panorama.mp4` in your output folder

## Technical Details

### FFmpeg Integration

The application now uses the bundled FFmpeg binary directly for optimal performance:
- **Concat Demuxer**: Uses FFmpeg's concat demuxer for lossless concatenation
- **Stream Copy**: No re-encoding - preserves original quality and ensures fast processing
- **Bundled Binary**: Includes ffmpeg.exe in the application bundle
- **Fallback Support**: Falls back to system FFmpeg if bundled version unavailable

### Input Selection Modes

#### Folder Mode (Recommended)
- Scans entire folder for RecM0* files
- Automatically includes all valid files
- Best for processing complete recording sessions

#### File Mode
- Multi-file selection dialog
- Manual control over which files to include
- Filters out non-RecM0 files automatically
- Best for selective merging or when files are in different locations

### File Processing Logic

1. **File Discovery**: 
   - Folder mode: Scans input folder for files matching `RecM0*` pattern
   - File mode: Processes user-selected files and filters for `RecM0*` pattern
2. **Timestamp Extraction**: Parses `YYYYMMDD_HHMMSS` from filenames
3. **Chronological Sorting**: Orders files from oldest to newest
4. **Video Merging**: Uses direct FFmpeg calls with concat demuxer (no re-encoding)
5. **Output Generation**: Saves merged result as `Panorama.mp4`

### Error Handling

The application handles various error scenarios:
- Missing or invalid input/output folders/files
- No valid video files found
- Invalid filename formats
- FFmpeg processing errors
- File permission issues
- Existing output file conflicts
- Mixed selection modes (prevents conflicts)
- FFmpeg binary availability checks

### GUI Features

- **Grey background with blue highlights** for modern appearance
- **Radio button selection** for input mode
- **Dynamic interface** that changes based on selected mode
- **Real-time logging** with timestamps
- **Progress bar** during processing
- **File count display** in file selection mode
- **Disabled controls** during processing to prevent conflicts
- **Confirmation dialogs** for file overwrites
- **Detailed error messages** for troubleshooting

## File Structure

```
Camera-Pan-Video-Combiner/
├── main.py                    # Main application code
├── setup.py                   # py2exe compilation script
├── requirements.txt           # Python dependencies
├── README.md                  # This documentation
├── install_and_run.bat        # Quick setup script
├── compile_to_exe.bat         # Compilation script
├── ffmpeg/                    # Bundled FFmpeg
│   └── bin/
│       ├── ffmpeg.exe         # FFmpeg binary
│       ├── ffprobe.exe        # FFprobe binary
│       └── ffplay.exe         # FFplay binary
└── dist/                      # Compiled executable (after compilation)
    └── CameraPanVideoCombiner.exe
```

## Troubleshooting

### Common Issues

**1. FFmpeg not found**
- The application includes a bundled FFmpeg binary at `ffmpeg/bin/ffmpeg.exe`
- If bundled FFmpeg fails, ensure system FFmpeg is installed and in PATH
- Check file permissions if on restrictive systems

**2. No video files found**
- Ensure files start with "RecM0" (case sensitive)
- Check that files follow the `RecM0X_YYYYMMDD_HHMMSS_` naming pattern
- Verify files are in supported formats (MP4, AVI, MOV)
- In file mode, the tool automatically filters out invalid files

**3. Compilation issues with py2exe**
- Ensure you're running on Windows
- Try running as administrator
- Check that all dependencies are installed

**4. File selection issues**
- File mode only accepts files starting with "RecM0"

**5. Video processing timeout**
- For very large files, the 5-minute timeout may be insufficient
- Consider splitting large video sets into smaller batches

## Version History

- **v1.1.0** - Added File Selection Mode with dual input options
- **v1.0.0** - Initial release with folder selection functionality

## License

This project is open source. See repository for license details.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the process log in the application
3. Create an issue in the repository

---

**Note**: This tool is designed specifically for merging panoramic camera recordings with the RecM0* naming convention. For other video formats or naming patterns, modifications to the code may be required. 