"""
Build script for creating Electron-compatible executable
Handles webrtcvad metadata issue
"""
import PyInstaller.__main__
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    os.path.join(script_dir, 'electron_transcriber.py'),
    '--name=transcriber',
    '--onefile',  # Create single executable
    '--console',  # Keep console for stdin/stdout
    
    # Hidden imports that PyInstaller might miss
    '--hidden-import=numpy',
    '--hidden-import=scipy',
    '--hidden-import=scipy.signal',
    '--hidden-import=webrtcvad',
    '--hidden-import=faster_whisper',
    '--hidden-import=torch',
    '--hidden-import=ctranslate2',
    '--hidden-import=tokenizers',
    '--hidden-import=pyaudio',
    
    # Collect data files
    '--collect-data=faster_whisper',
    '--collect-data=torch',
    
    # Collect binaries
    '--collect-binaries=pyaudio',
    
    # Exclude problematic modules to reduce size
    '--exclude-module=matplotlib',
    '--exclude-module=tkinter',
    '--exclude-module=pytest',
    '--exclude-module=pandas',
    '--exclude-module=tensorflow',
    '--exclude-module=cv2',
    '--exclude-module=sklearn',
    '--exclude-module=PIL',
    
    # Disable UPX compression (can cause issues)
    '--noupx',
    
    # Clean build
    '--clean',
    
    # Suppress warnings
    '--log-level=WARN',
])
