import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging

logging.basicConfig(level=logging.WARNING)

if __name__ == '__main__':
    print("=" * 60)
    print("ULTRA SENSITIVE TEST - DEVICE 34")
    print("=" * 60)

    def on_vad_start():
        print("\n>>> [VAD] Voice detected!")

    def on_recording_start():
        print(">>> [REC] Recording started")

    def on_recording_stop():
        print(">>> [REC] Recording stopped - transcribing...")

    def on_recorded_chunk(chunk):
        # Show that audio chunks are being received
        import numpy as np
        audio = np.frombuffer(chunk, dtype=np.int16)
        amp = np.max(np.abs(audio))
        if amp > 100:
            print(f"    Audio chunk: amplitude={amp}")

    try:
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=34,

            # ULTRA SENSITIVE SETTINGS
            silero_sensitivity=0.1,  # Very sensitive (default 0.4)
            webrtc_sensitivity=0,    # Most sensitive (default 3)
            post_speech_silence_duration=0.5,
            min_length_of_recording=0.2,

            # Callbacks
            on_vad_start=on_vad_start,
            on_recording_start=on_recording_start,
            on_recording_stop=on_recording_stop,
            on_recorded_chunk=on_recorded_chunk,

            spinner=False,
            level=logging.WARNING,
        )

        print("[OK] Recorder ready with ULTRA SENSITIVE settings\n")
        print("Instructions:")
        print("  1. Play YouTube video with speech")
        print("  2. You should see 'Audio chunk: amplitude=XXXX' messages")
        print("  3. If amplitude appears but no [VAD], VAD is broken")
        print("  4. If no amplitude at all, audio isn't being captured")
        print("\nWaiting...\n")

        count = 0
        while True:
            text = recorder.text()
            if text:
                count += 1
                print(f"\n{'='*60}")
                print(f"TRANSCRIPTION #{count}: {text}")
                print(f"{'='*60}\n")

    except KeyboardInterrupt:
        print(f"\n\nShutting down... (transcriptions: {count})")
        recorder.shutdown()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        recorder.shutdown()
