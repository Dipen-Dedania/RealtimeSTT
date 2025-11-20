import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio
import numpy as np
from faster_whisper import WhisperModel
import time

def capture_and_transcribe():
    """Capture audio and transcribe it manually to test the pipeline"""

    print("=" * 60)
    print("MANUAL CAPTURE + TRANSCRIBE TEST")
    print("=" * 60)

    # 1. Capture audio
    print("\n[1] Capturing audio from device 34...")
    p = pyaudio.PyAudio()

    stream = p.open(
        format=pyaudio.paInt16,
        channels=2,  # Stereo
        rate=48000,
        input=True,
        frames_per_buffer=1024,
        input_device_index=34,
    )

    print("    Recording for 3 seconds - SPEAK NOW!")
    print("    (Play YouTube video with speech)\n")

    frames = []
    for i in range(0, int(48000 / 1024 * 3)):  # 3 seconds
        data = stream.read(1024, exception_on_overflow=False)
        frames.append(data)
        if i % 50 == 0:
            print(f"    Recording... {i*1024/48000:.1f}s")

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("\n[2] Processing audio...")
    # Convert to numpy array
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    print(f"    Captured {len(audio_data)} samples")
    print(f"    Max amplitude: {np.max(np.abs(audio_data))}")

    # Convert stereo to mono
    audio_data = audio_data.reshape(-1, 2).mean(axis=1)
    print(f"    Converted to mono: {len(audio_data)} samples")

    # Resample to 16kHz
    from scipy.signal import resample
    target_length = int(len(audio_data) * 16000 / 48000)
    audio_16k = resample(audio_data, target_length)
    print(f"    Resampled to 16kHz: {len(audio_16k)} samples")

    # Normalize to float32 [-1, 1]
    audio_float = audio_16k.astype(np.float32) / 32768.0
    print(f"    Normalized to float32")

    # 3. Transcribe
    print("\n[3] Loading Whisper model...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")

    print("\n[4] Transcribing...")
    start = time.time()
    segments, info = model.transcribe(audio_float, language="en", beam_size=5)
    text = " ".join(seg.text for seg in segments).strip()
    elapsed = time.time() - start

    print(f"\n{'='*60}")
    print(f"TRANSCRIPTION (took {elapsed:.2f}s):")
    print(f"{'='*60}")
    if text:
        print(f"{text}")
    else:
        print("[EMPTY - No speech detected or transcription failed]")
    print(f"{'='*60}")

    print(f"\nLanguage detected: {info.language} (confidence: {info.language_probability:.2f})")

    if not text:
        print("\n[!] Transcription returned empty!")
        print("    Possible causes:")
        print("    - No speech in the audio")
        print("    - Audio too quiet")
        print("    - Background noise only")
        print("\nTry again with:")
        print("    - Clearer speech audio")
        print("    - Higher volume")
        print("    - Less background noise")

if __name__ == '__main__':
    try:
        capture_and_transcribe()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
