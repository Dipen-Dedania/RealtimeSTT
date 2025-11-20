import sys
import struct
import pyaudiowpatch as pyaudio
import numpy as np

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000

def find_loopback_device():
    """Find WASAPI loopback device"""
    p = pyaudio.PyAudio()
    
    # Get default WASAPI loopback device
    try:
        default_loopback = p.get_default_wasapi_loopback()
        if default_loopback:
            return default_loopback
    except:
        pass
    
    # Search for loopback devices
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            name = info['name'].lower()
            if 'loopback' in name or 'stereo mix' in name or 'what u hear' in name:
                return info
    
    return None

def capture_audio():
    """Capture system audio and stream to stdout"""
    p = pyaudio.PyAudio()
    
    device = find_loopback_device()
    if not device:
        print("No loopback device found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Using device: {device['name']}", file=sys.stderr)
    
    # Open stream
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=device['index'],
        frames_per_buffer=CHUNK
    )
    
    print("Starting audio capture...", file=sys.stderr)
    
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            # Write raw audio data to stdout
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    capture_audio()