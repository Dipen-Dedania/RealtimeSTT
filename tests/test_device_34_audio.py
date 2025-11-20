try:
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio
import numpy as np
import time

def test_device_34():
    """Quick test of device 34 audio capture"""
    p = pyaudio.PyAudio()

    print("="*60)
    print("TESTING DEVICE 34 - HEADPHONES LOOPBACK")
    print("="*60)

    dev = p.get_device_info_by_index(34)
    print(f"\nDevice: {dev['name']}")
    print(f"Sample rate: {int(dev['defaultSampleRate'])}")

    print("\n*** PLAY AUDIO NOW (YouTube with speech) ***")
    print("Testing for 5 seconds...\n")

    stream = p.open(
        format=pyaudio.paInt16,
        channels=2,
        rate=int(dev['defaultSampleRate']),
        input=True,
        frames_per_buffer=1024,
        input_device_index=34,
    )

    max_amp = 0
    chunks_with_audio = 0
    total = 0

    start = time.time()
    while time.time() - start < 5:
        data = stream.read(1024, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        amp = np.max(np.abs(audio))

        if amp > max_amp:
            max_amp = amp
        if amp > 100:
            chunks_with_audio += 1
        total += 1

        if total % 20 == 0:
            print(f"  Amplitude: {amp:6d} | Max: {max_amp:6d}")

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    print(f"Max amplitude: {max_amp}")
    print(f"Chunks with audio: {chunks_with_audio}/{total} ({100*chunks_with_audio/total:.1f}%)")

    if max_amp < 100:
        print("\n[X] NO AUDIO DETECTED!")
        print("    - Make sure audio is playing")
        print("    - Check volume is not muted")
        return False
    elif max_amp < 1000:
        print("\n[!] Audio is LOW but detected")
        print("    - Increase volume for better results")
        return True
    else:
        print("\n[OK] Audio looks good!")
        return True

if __name__ == '__main__':
    time.sleep(1)
    result = test_device_34()

    print("\n" + "="*60)
    if result:
        print("[OK] Ready to test with RealtimeSTT")
        print("\nRun: python tests/test_device_34.py")
    else:
        print("[X] Fix audio first")
        print("    - Unmute speakers")
        print("    - Play audio with speech")
    print("="*60)
