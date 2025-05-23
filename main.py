#!/usr/bin/env python3
"""
Camera-Pan Video Combiner Tool
A GUI application for merging panoramic video files from camera recordings.

This tool searches for video files with specific naming patterns (RecM0*),
sorts them chronologically, and merges them into a single panorama video
using the bundled ffmpeg binary.

Dependencies:
- tkinter (built-in)
- datetime (built-in)
- os (built-in)
- re (built-in)
- threading (built-in)
- glob (built-in)
- subprocess (built-in)
- shutil (built-in)
- pathlib (built-in)

Author: Camera Pan Video Combiner Tool
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re
import datetime
import threading
import glob
import sys
import subprocess
import shutil
from pathlib import Path
import tempfile


def get_bundled_ffmpeg_path():
    """Get the path to the bundled FFmpeg executable."""
    # Get the directory where this script is located
    if getattr(sys, 'frozen', False):
        # If running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # If running as Python script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to bundled FFmpeg
    bundled_ffmpeg = os.path.join(app_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')
    return bundled_ffmpeg


def check_ffmpeg_binary():
    """Check if FFmpeg binary is available (bundled first, then system PATH)."""
    # First, try the bundled FFmpeg
    bundled_ffmpeg = get_bundled_ffmpeg_path()
    
    if os.path.exists(bundled_ffmpeg):
        try:
            # Test the bundled FFmpeg
            result = subprocess.run([bundled_ffmpeg, '-version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0] if result.stdout else "Bundled FFmpeg found"
                return True, f"Using bundled FFmpeg: {version_line}", bundled_ffmpeg
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, Exception):
            pass  # Fall through to system FFmpeg check
    
    # If bundled FFmpeg doesn't work, try system FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else "System FFmpeg found"
            return True, f"Using system FFmpeg: {version_line}", 'ffmpeg'
        else:
            return False, "FFmpeg binary found but returned error", None
    except FileNotFoundError:
        return False, "FFmpeg binary not found", None
    except Exception as e:
        return False, f"Error checking FFmpeg: {str(e)}", None


class PanoramaCombiner:
    """Main application class for the Camera-Pan Video Combiner tool."""
    
    def __init__(self, root):
        """Initialize the application with GUI components."""
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_gui()
        self.check_ffmpeg_on_startup()
        
    def setup_window(self):
        """Configure the main window properties."""
        self.root.title("Camera-Pan Video Combiner")
        self.root.geometry("750x600")
        self.root.configure(bg='#E5E5E5')  # Light grey background
        self.root.resizable(True, True)
        
        # Center the window on screen
        self.center_window()
        
    def center_window(self):
        """Center the application window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_variables(self):
        """Initialize application variables."""
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.selected_files = []  # List to store selected files in file mode
        self.selection_mode = tk.StringVar(value="folder")  # "folder" or "files"
        self.progress_text = tk.StringVar()
        self.is_processing = False
        self.ffmpeg_available = False
        self.ffmpeg_path = None  # Store the path to FFmpeg executable
        
    def check_ffmpeg_on_startup(self):
        """Check if FFmpeg is available when the application starts."""
        self.ffmpeg_available, status_message, self.ffmpeg_path = check_ffmpeg_binary()
        
        if self.ffmpeg_available:
            self.log_message(f"✅ {status_message}")
        else:
            self.log_message(f"❌ FFmpeg check failed: {status_message}")
            self.log_message("⚠️  Video merging will not work until FFmpeg is available.")
        
    def setup_gui(self):
        """Create and arrange all GUI components."""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#E5E5E5', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Camera-Pan Video Combiner", 
            font=('Arial', 16, 'bold'),
            bg='#E5E5E5',
            fg='#2E5BBA'  # Blue color
        )
        title_label.pack(pady=(0, 20))
        
        # Selection mode frame
        self.create_selection_mode_section(main_frame)
        
        # Input selection frame (will be populated based on mode)
        self.input_frame = tk.Frame(main_frame, bg='#E5E5E5')
        self.input_frame.pack(fill=tk.X, pady=10)
        
        # Output folder selection
        self.create_folder_selection_section(
            main_frame,
            "Select Output Folder:",
            self.output_folder, 
            self.browse_output_folder
        )
        
        # Merge button
        self.merge_button = tk.Button(
            main_frame,
            text="🎬 Merge Videos",
            command=self.start_merge_process,
            font=('Arial', 12, 'bold'),
            bg='#2E5BBA',  # Blue background
            fg='white',
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.merge_button.pack(pady=20)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.pack(pady=(10, 10))
        
        # Log/Progress text area
        log_label = tk.Label(
            main_frame,
            text="Process Log:",
            font=('Arial', 10, 'bold'),
            bg='#E5E5E5',
            fg='#2E5BBA'
        )
        log_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Text area frame
        text_frame = tk.Frame(main_frame, bg='#E5E5E5')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text area with scrollbar
        self.log_text = tk.Text(
            text_frame,
            height=12,
            width=70,
            wrap=tk.WORD,
            bg='white',
            fg='black',
            font=('Consolas', 9),
            relief=tk.SUNKEN,
            borderwidth=2
        )
        
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial setup
        self.update_input_mode()
        
        # Initial log message
        self.log_message("Welcome to Camera-Pan Video Combiner!")
        self.log_message("Please select your input method and choose input/output locations to begin.")
        
    def create_selection_mode_section(self, parent):
        """Create the radio button section for selecting input mode."""
        mode_frame = tk.Frame(parent, bg='#E5E5E5')
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Label
        mode_label = tk.Label(
            mode_frame,
            text="Input Selection Method:",
            font=('Arial', 12, 'bold'),
            bg='#E5E5E5',
            fg='#2E5BBA'
        )
        mode_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Radio buttons frame
        radio_frame = tk.Frame(mode_frame, bg='#E5E5E5')
        radio_frame.pack(anchor=tk.W, padx=20)
        
        # Folder selection radio button
        folder_radio = tk.Radiobutton(
            radio_frame,
            text="📁 Select Folder (Recommended)",
            variable=self.selection_mode,
            value="folder",
            command=self.update_input_mode,
            font=('Arial', 10),
            bg='#E5E5E5',
            fg='black',
            selectcolor='#2E5BBA',
            activebackground='#E5E5E5'
        )
        folder_radio.pack(anchor=tk.W, pady=2)
        
        # File selection radio button
        files_radio = tk.Radiobutton(
            radio_frame,
            text="📄 Select Specific Files",
            variable=self.selection_mode,
            value="files",
            command=self.update_input_mode,
            font=('Arial', 10),
            bg='#E5E5E5',
            fg='black',
            selectcolor='#2E5BBA',
            activebackground='#E5E5E5'
        )
        files_radio.pack(anchor=tk.W, pady=2)
        
        # Description label
        self.mode_description = tk.Label(
            mode_frame,
            text="",
            font=('Arial', 9, 'italic'),
            bg='#E5E5E5',
            fg='#666666',
            wraplength=600
        )
        self.mode_description.pack(anchor=tk.W, pady=(8, 0), padx=20)
        
    def update_input_mode(self):
        """Update the input selection interface based on the selected mode."""
        # Clear the input frame
        for widget in self.input_frame.winfo_children():
            widget.destroy()
            
        mode = self.selection_mode.get()
        
        if mode == "folder":
            # Create folder selection interface
            self.create_input_folder_section()
            self.mode_description.config(
                text="Automatically finds and sorts all RecM0*.mp4 files in the selected folder."
            )
            # Clear file selection
            self.selected_files = []
            
        else:  # mode == "files"
            # Create file selection interface
            self.create_input_files_section()
            self.mode_description.config(
                text="Manually choose specific RecM0*.mp4 files. Only selected files will be merged."
            )
            # Clear folder selection
            self.input_folder.set("")
            
        # Update merge button state
        self.check_ready_to_merge()
        
    def create_input_folder_section(self):
        """Create the folder selection interface."""
        # Label
        label = tk.Label(
            self.input_frame,
            text="Select Input Folder:",
            font=('Arial', 10, 'bold'),
            bg='#E5E5E5',
            fg='#2E5BBA'
        )
        label.pack(anchor=tk.W)
        
        # Entry and button frame
        entry_frame = tk.Frame(self.input_frame, bg='#E5E5E5')
        entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Entry field
        entry = tk.Entry(
            entry_frame,
            textvariable=self.input_folder,
            font=('Arial', 9),
            relief=tk.SUNKEN,
            borderwidth=2,
            state='readonly'
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Browse button
        browse_button = tk.Button(
            entry_frame,
            text="Browse Folder",
            command=self.browse_input_folder,
            font=('Arial', 9),
            bg='#2E5BBA',
            fg='white',
            relief=tk.RAISED,
            borderwidth=1,
            padx=15
        )
        browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        
    def create_input_files_section(self):
        """Create the file selection interface."""
        # Label
        label = tk.Label(
            self.input_frame,
            text="Select Input Files:",
            font=('Arial', 10, 'bold'),
            bg='#E5E5E5',
            fg='#2E5BBA'
        )
        label.pack(anchor=tk.W)
        
        # File info frame
        info_frame = tk.Frame(self.input_frame, bg='#E5E5E5')
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        # File count label
        self.file_count_label = tk.Label(
            info_frame,
            text="No files selected",
            font=('Arial', 9),
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=2,
            anchor=tk.W,
            padx=5
        )
        self.file_count_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Browse button
        browse_button = tk.Button(
            info_frame,
            text="Browse Files",
            command=self.browse_input_files,
            font=('Arial', 9),
            bg='#2E5BBA',
            fg='white',
            relief=tk.RAISED,
            borderwidth=1,
            padx=15
        )
        browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        
    def create_folder_selection_section(self, parent, label_text, string_var, command):
        """Create a folder selection section with label, entry, and browse button."""
        frame = tk.Frame(parent, bg='#E5E5E5')
        frame.pack(fill=tk.X, pady=5)
        
        # Label
        label = tk.Label(
            frame,
            text=label_text,
            font=('Arial', 10, 'bold'),
            bg='#E5E5E5',
            fg='#2E5BBA'
        )
        label.pack(anchor=tk.W)
        
        # Entry and button frame
        entry_frame = tk.Frame(frame, bg='#E5E5E5')
        entry_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Entry field
        entry = tk.Entry(
            entry_frame,
            textvariable=string_var,
            font=('Arial', 9),
            relief=tk.SUNKEN,
            borderwidth=2,
            state='readonly'
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Browse button
        browse_button = tk.Button(
            entry_frame,
            text="Browse",
            command=command,
            font=('Arial', 9),
            bg='#2E5BBA',
            fg='white',
            relief=tk.RAISED,
            borderwidth=1,
            padx=15
        )
        browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        
    def browse_input_folder(self):
        """Open dialog to select input folder containing video files."""
        folder = filedialog.askdirectory(title="Select Input Folder (containing RecM0* videos)")
        if folder:
            self.input_folder.set(folder)
            self.log_message(f"Input folder selected: {folder}")
            self.check_ready_to_merge()
            
    def browse_input_files(self):
        """Open dialog to select specific video files."""
        files = filedialog.askopenfilenames(
            title="Select RecM0* Video Files",
            filetypes=[
                ("Video files", "*.mp4 *.MP4 *.avi *.AVI *.mov *.MOV"),
                ("MP4 files", "*.mp4 *.MP4"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            # Filter files to only include those starting with RecM0
            valid_files = []
            invalid_files = []
            
            for file_path in files:
                filename = os.path.basename(file_path)
                if filename.startswith('RecM0'):
                    valid_files.append(file_path)
                else:
                    invalid_files.append(filename)
                    
            self.selected_files = valid_files
            
            # Update UI
            if valid_files:
                count_text = f"{len(valid_files)} valid file(s) selected"
                self.file_count_label.config(text=count_text)
                self.log_message(f"Selected {len(valid_files)} valid video files")
                
                # Log selected files
                for i, file_path in enumerate(valid_files, 1):
                    filename = os.path.basename(file_path)
                    self.log_message(f"  {i}. {filename}")
                    
            else:
                self.file_count_label.config(text="No valid files selected")
                self.log_message("❌ No valid files selected!")
                
            # Log any invalid files
            if invalid_files:
                self.log_message(f"⚠️  Ignored {len(invalid_files)} files (don't start with 'RecM0'):")
                for filename in invalid_files:
                    self.log_message(f"     • {filename}")
                    
            self.check_ready_to_merge()
            
    def browse_output_folder(self):
        """Open dialog to select output folder for merged video."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            self.log_message(f"Output folder selected: {folder}")
            self.check_ready_to_merge()
            
    def check_ready_to_merge(self):
        """Enable merge button if input and output are properly selected and FFmpeg is available."""
        ready = False
        
        if self.output_folder.get() and not self.is_processing and self.ffmpeg_available:
            if self.selection_mode.get() == "folder":
                ready = bool(self.input_folder.get())
            else:  # files mode
                ready = bool(self.selected_files)
                
        if ready:
            self.merge_button.config(state=tk.NORMAL)
        else:
            self.merge_button.config(state=tk.DISABLED)
            
    def log_message(self, message):
        """Add a timestamped message to the log area."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_merge_process(self):
        """Start the video merging process in a separate thread."""
        if self.is_processing:
            return
            
        # Final FFmpeg check before starting
        if not self.ffmpeg_available:
            messagebox.showerror(
                "FFmpeg Not Available", 
                "FFmpeg is required for video merging but is not available.\n\n"
                "Please ensure the application is properly installed with all components."
            )
            return
            
        self.is_processing = True
        self.merge_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        
        # Run merge process in separate thread to keep GUI responsive
        thread = threading.Thread(target=self.merge_videos, daemon=True)
        thread.start()
        
    def find_video_files(self, input_source=None):
        """Find and parse video files based on the current selection mode."""
        mode = self.selection_mode.get()
        
        if mode == "folder":
            return self.find_video_files_in_folder(input_source)
        else:  # mode == "files"
            return self.process_selected_files()
            
    def find_video_files_in_folder(self, input_folder):
        """Find and parse video files starting with 'RecM0' in a folder."""
        self.log_message("Searching for video files in folder...")
        
        # Search for video files starting with RecM0
        video_extensions = ['*.mp4', '*.MP4', '*.avi', '*.AVI', '*.mov', '*.MOV']
        video_files = set()  # Use set to automatically deduplicate files
        
        for ext in video_extensions:
            pattern = os.path.join(input_folder, f"RecM0*{ext}")
            files = glob.glob(pattern)
            video_files.update(files)  # Add files to set (automatically deduplicates)
            
        # Convert set back to list
        video_files = list(video_files)
        
        if not video_files:
            self.log_message("❌ No video files starting with 'RecM0' found in folder!")
            return []
            
        self.log_message(f"Found {len(video_files)} unique video files starting with 'RecM0'")
        return self.parse_and_sort_files(video_files)
        
    def process_selected_files(self):
        """Process the manually selected files."""
        self.log_message("Processing selected video files...")
        
        if not self.selected_files:
            self.log_message("❌ No files selected!")
            return []
            
        self.log_message(f"Processing {len(self.selected_files)} selected files")
        return self.parse_and_sort_files(self.selected_files)
        
    def parse_and_sort_files(self, video_files):
        """Parse timestamps and sort video files chronologically."""
        # Parse and sort files by timestamp
        parsed_files = []
        timestamp_pattern = r'RecM0\d+_(\d{8})_(\d{6})'
        
        for file_path in video_files:
            filename = os.path.basename(file_path)
            match = re.search(timestamp_pattern, filename)
            
            if match:
                date_str = match.group(1)  # YYYYMMDD
                time_str = match.group(2)  # HHMMSS
                
                try:
                    # Parse datetime
                    dt = datetime.datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                    parsed_files.append((dt, file_path, filename))
                    self.log_message(f"✓ Parsed: {filename} -> {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                except ValueError as e:
                    self.log_message(f"⚠️  Could not parse timestamp in: {filename}")
            else:
                self.log_message(f"⚠️  Invalid filename format: {filename}")
                
        if not parsed_files:
            self.log_message("❌ No files with valid timestamp format found!")
            return []
            
        # Sort by datetime (oldest first)
        parsed_files.sort(key=lambda x: x[0])
        sorted_files = [file_path for _, file_path, _ in parsed_files]
        
        self.log_message(f"✓ Sorted {len(sorted_files)} files chronologically")
        for i, (dt, file_path, filename) in enumerate(parsed_files):
            self.log_message(f"  {i+1}. {filename}")
            
        return sorted_files
        
    def merge_videos_with_ffmpeg(self, video_files, output_path):
        """Merge video files using direct ffmpeg binary calls for concatenation without re-encoding."""
        self.log_message("Starting video merge process...")
        
        # Check FFmpeg availability one more time
        ffmpeg_available, status, ffmpeg_path = check_ffmpeg_binary()
        if not ffmpeg_available:
            self.log_message(f"❌ FFmpeg check failed: {status}")
            return False
        
        self.log_message(f"Using FFmpeg at: {ffmpeg_path}")
        
        try:
            # Create a temporary file list for ffmpeg concat demuxer
            # This is the fastest method for concatenating videos without re-encoding
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
                concat_file_path = f.name
                
                # Write file list in ffmpeg concat format
                self.log_message("Creating concat file list...")
                for i, video_file in enumerate(video_files):
                    # Escape file paths for ffmpeg (handle spaces and special characters)
                    escaped_path = video_file.replace('\\', '\\\\').replace("'", "\\'")
                    f.write(f"file '{escaped_path}'\n")
                    self.log_message(f"Added to list {i+1}/{len(video_files)}: {os.path.basename(video_file)}")
                
                self.log_message(f"✓ Created concat file list with {len(video_files)} videos")
            
            # Build ffmpeg command for concatenation without re-encoding
            self.log_message("Building ffmpeg command...")
            
            cmd = [
                ffmpeg_path,
                '-f', 'concat',           # Use concat demuxer
                '-safe', '0',             # Allow unsafe file paths
                '-i', concat_file_path,   # Input concat file
                '-c', 'copy',             # Copy streams without re-encoding
                '-avoid_negative_ts', 'make_zero',  # Handle timestamp issues
                '-y',                     # Overwrite output file if exists
                output_path              # Output file
            ]
            
            self.log_message(f"FFmpeg command: {' '.join(cmd)}")
            self.log_message("Executing ffmpeg process... (this may take a while)")
            
            # Run ffmpeg process
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                )
                
                if result.returncode == 0:
                    self.log_message("✅ Video merge completed successfully!")
                    
                    # Log some useful info from ffmpeg output
                    if result.stderr:
                        # Extract useful information from stderr (ffmpeg outputs info to stderr)
                        lines = result.stderr.split('\n')
                        for line in lines:
                            if 'frame=' in line and 'time=' in line:
                                # This is the progress line, just log the last one
                                continue
                            elif 'Duration:' in line or 'Stream' in line or 'Output' in line:
                                self.log_message(f"FFmpeg: {line.strip()}")
                    
                    return True
                    
                else:
                    error_msg = f"FFmpeg process failed with return code {result.returncode}"
                    if result.stdout:
                        error_msg += f"\nStdout: {result.stdout}"
                    if result.stderr:
                        error_msg += f"\nStderr: {result.stderr}"
                    self.log_message(f"❌ {error_msg}")
                    return False
                    
            except subprocess.TimeoutExpired:
                self.log_message("❌ FFmpeg process timed out (over 5 minutes)")
                return False
                
            except Exception as e:
                self.log_message(f"❌ Error running FFmpeg process: {str(e)}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Unexpected error during merge: {str(e)}")
            self.log_message(f"Error type: {type(e).__name__}")
            
            # Additional debugging info
            self.log_message("Debugging information:")
            self.log_message(f"  - Using FFmpeg path: {ffmpeg_path}")
            self.log_message(f"  - Bundled FFmpeg path: {get_bundled_ffmpeg_path()}")
            self.log_message(f"  - Bundled FFmpeg exists: {os.path.exists(get_bundled_ffmpeg_path())}")
            
            return False
            
        finally:
            # Clean up temporary concat file
            try:
                if 'concat_file_path' in locals() and os.path.exists(concat_file_path):
                    os.unlink(concat_file_path)
                    self.log_message("✓ Cleaned up temporary files")
            except Exception as e:
                self.log_message(f"⚠️  Warning: Could not clean up temporary file: {str(e)}")
            
    def merge_videos(self):
        """Main merge process - find files, sort, and merge them."""
        try:
            output_folder = self.output_folder.get()
            
            # Validate output folder
            if not os.path.exists(output_folder):
                self.log_message("❌ Output folder does not exist!")
                return
                
            # Get input source based on mode
            if self.selection_mode.get() == "folder":
                input_folder = self.input_folder.get()
                if not os.path.exists(input_folder):
                    self.log_message("❌ Input folder does not exist!")
                    return
                video_files = self.find_video_files(input_folder)
            else:  # files mode
                video_files = self.find_video_files()
                
            if not video_files:
                mode_text = "folder" if self.selection_mode.get() == "folder" else "selected files"
                messagebox.showerror(
                    "Error", 
                    f"No valid video files found in {mode_text}!\n\n"
                    "Please ensure you have video files starting with 'RecM0' and following the naming pattern:\n"
                    "RecM05_YYYYMMDD_HHMMSS_..."
                )
                return
                
            # Create output path
            output_path = os.path.join(output_folder, "Panorama.mp4")
            
            # Check if output file already exists
            if os.path.exists(output_path):
                response = messagebox.askyesno(
                    "File Exists", 
                    f"The file 'Panorama.mp4' already exists in the output folder.\n\nDo you want to overwrite it?"
                )
                if not response:
                    self.log_message("❌ Merge cancelled by user")
                    return
                    
            # Merge videos
            success = self.merge_videos_with_ffmpeg(video_files, output_path)
            
            if success:
                # Show completion message
                self.log_message("🎉 MERGE COMPLETE!")
                self.log_message(f"📁 Output saved to: {output_path}")
                
                # Show success dialog
                messagebox.showinfo(
                    "Success", 
                    "✅ Merging complete! You can now upload the video to VideoArena.\n\n"
                    f"Output file: Panorama.mp4\nLocation: {output_folder}"
                )
            else:
                messagebox.showerror("Error", "Video merging failed! Please check the log for details.")
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
            
        finally:
            # Reset UI state
            self.is_processing = False
            self.progress_bar.stop()
            self.check_ready_to_merge()


def main():
    """Main entry point for the application."""
    try:
        # Create and run the application
        root = tk.Tk()
        app = PanoramaCombiner(root)
        
        # Handle window closing
        def on_closing():
            if app.is_processing:
                if messagebox.askokcancel("Quit", "A merge process is running. Do you really want to quit?"):
                    root.destroy()
            else:
                root.destroy()
                
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Failed to start application:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
