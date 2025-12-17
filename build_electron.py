"""
Build script for creating Electron-compatible executable
Handles webrtcvad metadata issue
"""
import PyInstaller.__main__
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to local RealtimeSTT package
realtimestt_path = os.path.join(script_dir, 'RealtimeSTT')

PyInstaller.__main__.run([
    os.path.join(script_dir, 'electron_transcriber.py'),
    '--name=transcriber',
    '--onefile',  # Create single executable
    '--console',  # Keep console for stdin/stdout
    
    # Add the script directory to Python path so RealtimeSTT can be found
    f'--paths={script_dir}',
    
    # Use local hooks
    f'--additional-hooks-dir={os.path.join(script_dir, "hooks")}',
    
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
    
    # Include local RealtimeSTT package
    '--hidden-import=RealtimeSTT',
    '--hidden-import=RealtimeSTT.audio_recorder',
    '--hidden-import=RealtimeSTT.audio_input',
    '--hidden-import=RealtimeSTT.safepipe',
    
    # Additional dependencies for RealtimeSTT
    '--hidden-import=openwakeword',
    '--hidden-import=openwakeword.model',
    '--hidden-import=pvporcupine',
    '--hidden-import=silero',
    '--hidden-import=halo',
    '--hidden-import=colorama',
    '--hidden-import=soundfile',
    
    # Collect all (binaries, data, hidden imports)
    '--collect-all=faster_whisper',
    '--collect-all=torch',
    '--collect-all=ctranslate2',
    '--collect-all=openwakeword',
    '--collect-all=pvporcupine',
    '--collect-all=silero',
    
    # Collect binaries
    '--collect-binaries=pyaudio',
    
    # Add RealtimeSTT data files (warmup_audio.wav etc)
    f'--add-data={realtimestt_path};RealtimeSTT',
    
    # Include sklearn (required by openwakeword)
    '--hidden-import=sklearn',
    '--hidden-import=sklearn.tree',
    '--collect-all=sklearn',
    
    # Exclude problematic modules to reduce size
    '--exclude-module=matplotlib',
    '--exclude-module=tkinter',
    '--exclude-module=pytest',
    '--exclude-module=pandas',
    '--exclude-module=tensorflow',
    '--exclude-module=cv2',
    '--exclude-module=PIL',
    
    # Disable UPX compression (can cause issues)
    '--noupx',
    
    # Clean build
    '--clean',
    
    # Suppress warnings
    '--log-level=WARN',
])
