import sys
import struct
import pyaudiowpatch as pyaudio
import numpy as np
import wave

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
OUTPUT_FILENAME = "loopback_user_test.wav"
RECORD_SECONDS = 5

def find_loopback_device():
    """Find WASAPI loopback device"""
    p = pyaudio.PyAudio()
    
    # Get default WASAPI loopback device
    try:
        default_loopback = p.get_default_wasapi_loopback()
        if default_loopback:
            print(f"Found default loopback device: {default_loopback['name']}")
            return default_loopback
    except Exception as e:
        print(f"Error getting default loopback: {e}")
        pass
    
    # Search for loopback devices
    print("Searching for loopback devices manually...")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        # print(f"Checking device {i}: {info['name']}")
        if info['maxInputChannels'] > 0:
            name = info['name'].lower()
            if 'loopback' in name or 'stereo mix' in name or 'what u hear' in name:
                return info
    
    return None

def capture_audio():
    """Capture system audio and save to file"""
    p = pyaudio.PyAudio()
    
    device = find_loopback_device()
    if not device:
        print("No loopback device found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Using device: {device['name']} (Index: {device['index']})", file=sys.stderr)
    
    # Open stream
    # Note: The user script didn't use as_loopback=True, but let's see if it works.
    # If get_default_wasapi_loopback returns a specific loopback device, maybe it's enough.
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device['index'],
            frames_per_buffer=CHUNK
        )
    except Exception as e:
        print(f"Error opening stream: {e}")
        # Try with as_loopback=True if the above fails, though the user said it worked without.
        try:
            print("Retrying with as_loopback=True...")
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device['index'],
                frames_per_buffer=CHUNK,
                as_loopback=True
            )
        except Exception as e2:
            print(f"Error opening stream with as_loopback=True: {e2}")
            return

    print("Starting audio capture...", file=sys.stderr)
    
    frames = []
    try:
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error recording: {e}")
    finally:
        print("Stopping recording...")
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Saved to {OUTPUT_FILENAME}")

if __name__ == "__main__":
    capture_audio()
