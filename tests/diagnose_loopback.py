import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio
import numpy as np
import time

def list_loopback_devices():
    """List all available loopback devices"""
    p = pyaudio.PyAudio()
    print("=" * 60)
    print("AVAILABLE LOOPBACK DEVICES:")
    print("=" * 60)

    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        name = dev['name']
        if 'loopback' in name.lower() or dev.get('maxInputChannels', 0) > 0:
            print(f"\nDevice {i}: {name}")
            print(f"  Max Input Channels: {dev.get('maxInputChannels', 0)}")
            print(f"  Default Sample Rate: {dev.get('defaultSampleRate', 0)}")
            if 'loopback' in name.lower():
                print("  *** LOOPBACK DEVICE ***")

    p.terminate()
    print("\n" + "=" * 60)

def test_audio_capture(device_index, duration=5):
    """Test if we're actually capturing audio from the device"""
    p = pyaudio.PyAudio()

    print(f"\nTesting audio capture from device {device_index}...")
    dev = p.get_device_info_by_index(device_index)
    print(f"Device name: {dev['name']}")

    sample_rate = int(dev.get('defaultSampleRate', 48000))
    channels = 2  # Most loopback devices use stereo

    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=1024,
            input_device_index=device_index,
        )

        print(f"\n{'='*60}")
        print(f"RECORDING FROM DEVICE {device_index} FOR {duration} SECONDS")
        print(f"{'='*60}")
        print("\n*** PLAY SOME AUDIO NOW (YouTube, music, etc.) ***\n")

        max_amplitude = 0
        chunks_with_audio = 0
        total_chunks = 0

        start_time = time.time()
        while time.time() - start_time < duration:
            data = stream.read(1024, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # Calculate audio levels
            amplitude = np.max(np.abs(audio_data))
            if amplitude > max_amplitude:
                max_amplitude = amplitude

            if amplitude > 100:  # Threshold for "audio detected"
                chunks_with_audio += 1

            total_chunks += 1

            # Print progress
            elapsed = time.time() - start_time
            if int(elapsed) != int(elapsed - 0.1):  # Print roughly every second
                print(f"[{elapsed:.1f}s] Current amplitude: {amplitude:6d}, Max: {max_amplitude:6d}")

        stream.stop_stream()
        stream.close()
        p.terminate()

        print(f"\n{'='*60}")
        print("RESULTS:")
        print(f"{'='*60}")
        print(f"Max amplitude detected: {max_amplitude}")
        print(f"Chunks with audio: {chunks_with_audio}/{total_chunks}")
        print(f"Percentage with audio: {100*chunks_with_audio/total_chunks:.1f}%")

        if max_amplitude < 100:
            print("\n⚠️  WARNING: No significant audio detected!")
            print("   Possible issues:")
            print("   - No audio is playing")
            print("   - Wrong device selected")
            print("   - Audio routing not configured correctly")
        elif max_amplitude < 1000:
            print("\n⚠️  WARNING: Audio levels are very low!")
            print("   This might not trigger voice activity detection.")
        else:
            print("\n✓ Audio is being captured successfully!")

        return max_amplitude > 100

    except Exception as e:
        print(f"\n❌ ERROR: Failed to capture audio: {e}")
        p.terminate()
        return False

def test_vad_sensitivity():
    """Test voice activity detection thresholds"""
    print("\n" + "=" * 60)
    print("VAD SENSITIVITY INFO")
    print("=" * 60)
    print("\nDefault VAD settings in RealtimeSTT:")
    print("  - silero_sensitivity: 0.4 (lower = more sensitive)")
    print("  - webrtc_sensitivity: 3 (0-3, higher = less sensitive)")
    print("\nFor loopback audio, you may need:")
    print("  - Lower silero_sensitivity (e.g., 0.2-0.3)")
    print("  - Lower webrtc_sensitivity (e.g., 1-2)")
    print("=" * 60)

if __name__ == '__main__':
    print("=" * 60)
    print("LOOPBACK AUDIO DIAGNOSTIC TOOL")
    print("=" * 60)

    # Step 1: List devices
    list_loopback_devices()

    # Step 2: Get device index from user or use default
    device_str = input("\nEnter device index to test (or press Enter for device 38): ").strip()
    device_index = int(device_str) if device_str else 38

    # Step 3: Test audio capture
    audio_ok = test_audio_capture(device_index, duration=5)

    # Step 4: Show VAD info
    test_vad_sensitivity()

    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    if audio_ok:
        print("✓ Audio capture is working!")
        print("\nIf transcription still doesn't work, try adjusting VAD settings:")
        print("  recorder = AudioToTextRecorder(")
        print("      use_loopback=True,")
        print("      input_device_index={},".format(device_index))
        print("      silero_sensitivity=0.2,  # More sensitive")
        print("      webrtc_sensitivity=2,    # More sensitive")
        print("      spinner=True,")
        print("  )")
    else:
        print("❌ Audio capture is NOT working!")
        print("\nTroubleshooting steps:")
        print("1. Verify device index is correct")
        print("2. Play audio while testing")
        print("3. Check Windows audio settings")
        print("4. Make sure VB-Cable is installed and configured")
    print("=" * 60)
