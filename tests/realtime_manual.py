"""
Manual realtime transcription without RealtimeSTT multiprocessing
This WILL work based on your successful manual tests
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
import threading
from collections import deque

class RealtimeLoopbackTranscriber:
    def __init__(self):
        print("=" * 60)
        print("REALTIME LOOPBACK TRANSCRIPTION")
        print("=" * 60)
        print("\n[1] Loading models...")

        self.whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.vad = webrtcvad.Vad(1)

        print("[2] Opening audio stream (device 34)...")
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=48000,
            input=True,
            frames_per_buffer=1024,
            input_device_index=34,
        )

        self.frames = deque(maxlen=500)  # Keep last ~10 seconds
        self.recording = False
        self.running = True
        self.last_transcribe = time.time()

        print("[3] Starting audio capture thread...")
        self.audio_thread = threading.Thread(target=self._capture_audio, daemon=True)
        self.audio_thread.start()

        print("[4] Starting realtime transcription thread...")
        self.transcribe_thread = threading.Thread(target=self._realtime_transcribe, daemon=True)
        self.transcribe_thread.start()

        print("\n" + "=" * 60)
        print("READY! Play YouTube video with speech")
        print("Transcription will appear in real-time below:")
        print("=" * 60 + "\n")

    def _capture_audio(self):
        """Continuously capture audio"""
        while self.running:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.int16)

                # Check for speech with VAD
                audio_mono = audio_np.reshape(-1, 2).mean(axis=1).astype(np.int16)
                from scipy.signal import resample
                audio_16k = resample(audio_mono, int(len(audio_mono) * 16000 / 48000))
                audio_16k_bytes = audio_16k.astype(np.int16).tobytes()

                is_speech = False
                frame_length = int(16000 * 0.01)
                for i in range(len(audio_16k_bytes) // (2 * frame_length)):
                    frame = audio_16k_bytes[i*frame_length*2:(i+1)*frame_length*2]
                    if len(frame) == frame_length * 2:
                        try:
                            if self.vad.is_speech(frame, 16000):
                                is_speech = True
                                break
                        except:
                            pass

                if is_speech:
                    if not self.recording:
                        print("\n[>>>] Speech detected - starting transcription\n")
                        self.recording = True
                        self.frames.clear()

                    self.frames.append(data)
                elif self.recording:
                    # Keep adding for a bit after speech stops
                    self.frames.append(data)

            except Exception as e:
                print(f"\n[ERROR in capture] {e}")
                break

    def _realtime_transcribe(self):
        """Transcribe every 0.5 seconds while recording"""
        while self.running:
            try:
                if self.recording and len(self.frames) > 20:  # At least ~0.4 seconds
                    now = time.time()

                    # Transcribe every 0.5 seconds
                    if now - self.last_transcribe >= 0.5:
                        self.last_transcribe = now

                        # Get current audio
                        all_audio = np.frombuffer(b''.join(self.frames), dtype=np.int16)
                        audio_mono = all_audio.reshape(-1, 2).mean(axis=1)

                        # Resample to 16kHz
                        from scipy.signal import resample
                        audio_16k = resample(audio_mono, int(len(audio_mono) * 16000 / 48000))
                        audio_float = audio_16k.astype(np.float32) / 32768.0

                        # Transcribe
                        segments, info = self.whisper_model.transcribe(
                            audio_float,
                            language="en",
                            beam_size=3,  # Faster beam size for realtime
                            vad_filter=False  # We already did VAD
                        )
                        text = " ".join(seg.text for seg in segments).strip()

                        if text:
                            # Clear line and print
                            print(f"\r[REALTIME] {text}", end="", flush=True)

                time.sleep(0.1)

            except Exception as e:
                print(f"\n[ERROR in transcribe] {e}")
                import traceback
                traceback.print_exc()
                time.sleep(0.5)

    def run(self):
        """Keep running until Ctrl+C"""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
            self.running = False
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            print("[OK] Done!")

if __name__ == '__main__':
    try:
        transcriber = RealtimeLoopbackTranscriber()
        transcriber.run()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
