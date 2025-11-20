import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging
import threading
import time

logging.basicConfig(level=logging.WARNING)

if __name__ == '__main__':
    print("=" * 60)
    print("TRANSCRIPTION TIMEOUT TEST")
    print("=" * 60)

    transcription_started = False
    transcription_timeout = None

    def on_recording_stop():
        global transcription_started, transcription_timeout
        print(">>> [REC] Recording stopped - transcribing...")
        transcription_started = True
        transcription_timeout = time.time()

    def on_transcription_start(audio):
        print(f">>> [TRANS] Transcription started (audio: {len(audio)} samples)")

    try:
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=34,

            silero_sensitivity=0.1,
            webrtc_sensitivity=0,
            post_speech_silence_duration=0.5,
            min_length_of_recording=0.2,

            on_recording_stop=on_recording_stop,
            on_transcription_start=on_transcription_start,

            spinner=False,
            level=logging.WARNING,
        )

        print("[OK] Recorder ready\n")
        print("1. Play YouTube video with speech for 2-3 seconds")
        print("2. Pause/stop the video")
        print("3. Wait and watch...\n")

        count = 0
        timeout_warned = False

        while True:
            # Start a background thread to monitor timeout
            def check_timeout():
                global timeout_warned
                while transcription_started and not timeout_warned:
                    if time.time() - transcription_timeout > 5:
                        print("\n[!] WARNING: Transcription taking >5 seconds!")
                        print("    This suggests the transcription worker is hanging")
                        timeout_warned = True
                        break
                    time.sleep(0.5)

            if transcription_started and not timeout_warned:
                threading.Thread(target=check_timeout, daemon=True).start()

            text = recorder.text()

            if text:
                count += 1
                elapsed = time.time() - transcription_timeout if transcription_timeout else 0
                print(f"\n{'='*60}")
                print(f"SUCCESS! Transcription took {elapsed:.1f}s")
                print(f"{'='*60}")
                print(f"{text}")
                print(f"{'='*60}\n")

                # Reset
                transcription_started = False
                transcription_timeout = None
                timeout_warned = False
            elif transcription_started:
                # Empty result after transcription
                print("\n[!] Transcription returned empty string")
                print("    Possible causes:")
                print("    - Audio too short (increase min_length_of_recording)")
                print("    - No speech detected by Whisper model")
                print("    - Audio quality too poor")

                # Reset
                transcription_started = False
                transcription_timeout = None
                timeout_warned = False

    except KeyboardInterrupt:
        print(f"\n\nShutting down... (transcriptions: {count})")
        recorder.shutdown()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        recorder.shutdown()
