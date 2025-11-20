import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio
import numpy as np
import time

def test_audio_capture(device_index=38, duration=3):
    """Test if we're actually capturing audio from the device"""
    p = pyaudio.PyAudio()

    print(f"\n{'='*60}")
    print(f"TESTING AUDIO CAPTURE FROM DEVICE {device_index}")
    print(f"{'='*60}")

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

        print(f"\n*** MAKE SURE AUDIO IS PLAYING (YouTube, music, etc.) ***")
        print(f"Recording for {duration} seconds...\n")

        max_amplitude = 0
        chunks_with_audio = 0
        total_chunks = 0
        amplitudes = []

        start_time = time.time()
        while time.time() - start_time < duration:
            data = stream.read(1024, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # Calculate audio levels
            amplitude = np.max(np.abs(audio_data))
            amplitudes.append(amplitude)

            if amplitude > max_amplitude:
                max_amplitude = amplitude

            if amplitude > 100:  # Threshold for "audio detected"
                chunks_with_audio += 1

            total_chunks += 1

            # Print progress every ~0.5 seconds
            if total_chunks % 20 == 0:
                print(f"  Amplitude: {amplitude:6d} | Max so far: {max_amplitude:6d}")

        stream.stop_stream()
        stream.close()
        p.terminate()

        print(f"\n{'='*60}")
        print("RESULTS:")
        print(f"{'='*60}")
        print(f"Max amplitude detected: {max_amplitude}")
        print(f"Average amplitude: {np.mean(amplitudes):.0f}")
        print(f"Chunks with audio (>100): {chunks_with_audio}/{total_chunks} ({100*chunks_with_audio/total_chunks:.1f}%)")

        if max_amplitude < 100:
            print("\n[X] PROBLEM: No significant audio detected!")
            print("\nPossible causes:")
            print("  1. No audio is currently playing")
            print("  2. Wrong device selected (not the one audio is routed to)")
            print("  3. VB-Cable not properly configured in Windows")
            print("\nTo fix:")
            print("  - Make sure audio is playing")
            print("  - Set your application's audio output to 'CABLE Input'")
            print("  - Or try device 34 (Headphones Loopback) instead")
            return False
        elif max_amplitude < 1000:
            print("\n[!] WARNING: Audio levels are VERY LOW!")
            print(f"   Max amplitude: {max_amplitude} (should be >1000 for reliable VAD)")
            print("\nThis will likely NOT trigger voice activity detection!")
            print("\nTo fix:")
            print("  - Increase system volume")
            print("  - Lower VAD sensitivity thresholds")
            return False
        else:
            print("\n[OK] Audio capture is working!")
            print(f"   Amplitude levels look good for VAD triggering")
            return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        p.terminate()
        return False

if __name__ == '__main__':
    print("="*60)
    print("QUICK LOOPBACK AUDIO TEST")
    print("="*60)
    print("\n*** IMPORTANT: Play some audio NOW (YouTube, music, speech) ***")
    print("    The test will start in 2 seconds...\n")
    time.sleep(2)

    result = test_audio_capture(device_index=38, duration=3)

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    if result:
        print("\n[OK] Audio is working! Now test with RealtimeSTT...")
        print("\nRun: python tests/dipen_debug.py")
    else:
        print("\n[X] Fix audio capture first before using RealtimeSTT")
        print("\nTry:")
        print("  - Device 34 (Headphones Loopback)")
        print("  - Device 36 (CABLE In 16ch Loopback)")
    print("="*60)
