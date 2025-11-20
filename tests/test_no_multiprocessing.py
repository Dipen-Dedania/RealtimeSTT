"""
Test if the issue is with multiprocessing by manually feeding audio
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio
import numpy as np
from faster_whisper import WhisperModel
import webrtcvad
import torch
import time

def test_without_multiprocessing():
    """Manually implement the audio capture + VAD + transcription pipeline"""

    print("=" * 60)
    print("MANUAL PIPELINE (NO MULTIPROCESSING)")
    print("=" * 60)
    print("\nThis tests the same pipeline but without multiprocessing")
    print("to see if that's the issue.\n")

    # Load models
    print("[1] Loading models...")
    whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
    vad = webrtcvad.Vad(1)  # Sensitivity 1
    silero_vad, _ = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad", verbose=False, onnx=False)
    print("    Models loaded!\n")

    # Open audio stream
    print("[2] Opening audio stream (device 34)...")
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=2,
        rate=48000,
        input=True,
        frames_per_buffer=1024,
        input_device_index=34,
    )
    print("    Stream opened!\n")

    print("[3] Listening for speech...")
    print("    Play YouTube video with speech\n")

    frames = []
    recording = False
    silence_start = None
    SILENCE_DURATION = 0.8  # seconds

    try:
        while True:
            # Read audio
            data = stream.read(1024, exception_on_overflow=False)
            audio_np = np.frombuffer(data, dtype=np.int16)

            # Convert to mono and resample to 16kHz for VAD
            audio_mono = audio_np.reshape(-1, 2).mean(axis=1).astype(np.int16)
            from scipy.signal import resample
            audio_16k = resample(audio_mono, int(len(audio_mono) * 16000 / 48000))
            audio_16k_bytes = audio_16k.astype(np.int16).tobytes()

            # VAD check
            is_speech = False
            try:
                # WebRTC VAD (check frames)
                frame_length = int(16000 * 0.01)  # 10ms
                for i in range(len(audio_16k_bytes) // (2 * frame_length)):
                    frame = audio_16k_bytes[i*frame_length*2:(i+1)*frame_length*2]
                    if len(frame) == frame_length * 2:
                        if vad.is_speech(frame, 16000):
                            is_speech = True
                            break
            except:
                pass

            # If speech detected, start/continue recording
            if is_speech:
                if not recording:
                    print("    [VAD] Speech detected - recording started")
                    recording = True
                    frames = []

                frames.append(data)
                silence_start = None

            # If no speech and we're recording, check for silence duration
            elif recording:
                if silence_start is None:
                    silence_start = time.time()
                    print("    [VAD] Silence detected - waiting...")

                if time.time() - silence_start >= SILENCE_DURATION:
                    print("    [VAD] Silence duration met - stopping\n")

                    # Transcribe
                    print("    [TRANS] Transcribing...")
                    all_audio = np.frombuffer(b''.join(frames), dtype=np.int16)
                    audio_mono = all_audio.reshape(-1, 2).mean(axis=1)
                    audio_16k = resample(audio_mono, int(len(audio_mono) * 16000 / 48000))
                    audio_float = audio_16k.astype(np.float32) / 32768.0

                    segments, info = whisper_model.transcribe(audio_float, language="en", beam_size=5)
                    text = " ".join(seg.text for seg in segments).strip()

                    print("\n" + "="*60)
                    print("TRANSCRIPTION:")
                    print("="*60)
                    if text:
                        print(text)
                        print("="*60)
                        print("\n[OK] Success! Press Ctrl+C to stop or continue...")
                    else:
                        print("[EMPTY]")
                        print("="*60)

                    # Reset
                    recording = False
                    silence_start = None
                    frames = []
                    print("\n[3] Listening for more speech...\n")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\nStopping...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[OK] Done!")

if __name__ == '__main__':
    try:
        test_without_multiprocessing()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
