"""
Quick loopback test - plays audio through speakers and captures it
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
try:
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio
import wave

print("=" * 70)
print("QUICK LOOPBACK TEST")
print("=" * 70)
print("\nThis will:")
print("1. Play test audio through your DEFAULT speakers")
print("2. Capture it via loopback")
print("3. Transcribe what it hears")
print("\nStarting in 3 seconds...\n")

# Check which device is the default output
p = pyaudio.PyAudio()
try:
    default_output = p.get_default_output_device_info()
    print(f"Default output device: {default_output['name']}")
    print(f"If this is your headphones, audio won't be captured!")
    print(f"Temporarily unplug headphones or change default output.\n")
except:
    pass
p.terminate()

time.sleep(3)

# Flag to control audio playback
keep_playing = True

def play_test_audio():
    """Play continuous test audio"""
    import numpy as np

    p = pyaudio.PyAudio()

    # Generate test audio - beeping pattern with voice-like frequencies
    sample_rate = 16000
    duration = 2  # seconds per phrase

    test_phrases = [
        "This is a test of the loopback audio system.",
        "If you can read this, loopback is working correctly.",
        "Testing one two three four five."
    ]

    print("\n[AUDIO PLAYER] Starting audio playback...")

    try:
        # Open output stream on default device
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            output=True,
        )

        phrase_index = 0
        while keep_playing:
            # Generate a tone burst (simulating speech)
            t = np.linspace(0, duration, int(sample_rate * duration))

            # Mix of frequencies to simulate speech
            signal = (
                0.3 * np.sin(2 * np.pi * 200 * t) +  # Low frequency
                0.3 * np.sin(2 * np.pi * 800 * t) +  # Mid frequency
                0.2 * np.sin(2 * np.pi * 1500 * t)   # High frequency
            )

            # Add amplitude modulation (like speech patterns)
            envelope = np.sin(2 * np.pi * 2 * t) * 0.5 + 0.5
            signal = signal * envelope

            # Convert to int16
            audio_data = (signal * 32767 * 0.5).astype(np.int16)

            print(f"[AUDIO PLAYER] Playing: {test_phrases[phrase_index]}")
            stream.write(audio_data.tobytes())

            phrase_index = (phrase_index + 1) % len(test_phrases)
            time.sleep(0.5)  # Gap between phrases

    except Exception as e:
        print(f"[AUDIO PLAYER] Error: {e}")
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()
        print("[AUDIO PLAYER] Stopped")

def run_transcription():
    """Run the transcription with loopback"""
    from RealtimeSTT import AudioToTextRecorder

    print("\n[TRANSCRIBER] Initializing recorder with loopback...")

    # Try default loopback first
    recorder = AudioToTextRecorder(
        use_loopback=True,
        spinner=False,  # Disable spinner for cleaner output
        model="tiny",   # Fast model for testing
    )

    print("[TRANSCRIBER] Ready! Listening for loopback audio...")
    print("=" * 70)
    print("TRANSCRIPTIONS WILL APPEAR BELOW:")
    print("=" * 70)

    transcription_count = 0
    max_transcriptions = 3

    try:
        while transcription_count < max_transcriptions:
            text = recorder.text()

            if text:
                transcription_count += 1
                print(f"\n[{transcription_count}/{max_transcriptions}] TRANSCRIBED: {text}")
                print("-" * 70)

        print("\n[TRANSCRIBER] Captured 3 transcriptions! Test complete.")

    except KeyboardInterrupt:
        print("\n[TRANSCRIBER] Interrupted by user")
    finally:
        global keep_playing
        keep_playing = False
        recorder.shutdown()
        print("[TRANSCRIBER] Shutdown complete")

if __name__ == '__main__':
    # Start audio playback in background thread
    audio_thread = threading.Thread(target=play_test_audio, daemon=True)
    audio_thread.start()

    # Give audio time to start
    time.sleep(2)

    try:
        # Run transcription in main thread
        run_transcription()
    except KeyboardInterrupt:
        print("\nTest interrupted!")
    finally:
        keep_playing = False
        time.sleep(1)

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nIf you saw transcriptions above, loopback is WORKING!")
    print("If not, check that audio went through speakers (not headphones)")
