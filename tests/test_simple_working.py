import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging

# Suppress debug noise
logging.basicConfig(level=logging.WARNING)

if __name__ == '__main__':
    print("=" * 60)
    print("SIMPLE WORKING TEST")
    print("=" * 60)

    recorder = None

    try:
        print("\n[1] Initializing recorder...")
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=34,

            # Settings that worked in manual test
            silero_sensitivity=0.2,
            webrtc_sensitivity=1,
            post_speech_silence_duration=0.8,
            min_length_of_recording=0.5,  # At least 0.5 seconds

            spinner=False,
            level=logging.WARNING,
        )

        print("[2] Recorder ready!\n")
        print("Instructions:")
        print("  - Play YouTube video with CLEAR SPEECH")
        print("  - Let it play for 2-3 seconds")
        print("  - STOP/PAUSE the video")
        print("  - Wait 1-2 seconds")
        print("  - You should see transcription")
        print("\nPress Ctrl+C after getting transcription\n")
        print("="*60)

        transcription_count = 0
        max_tries = 10  # Try up to 10 times

        for attempt in range(max_tries):
            print(f"\n[Attempt {attempt + 1}/{max_tries}] Waiting for speech...")

            try:
                text = recorder.text()

                if text:
                    transcription_count += 1
                    print("\n" + "="*60)
                    print(f"SUCCESS! TRANSCRIPTION #{transcription_count}:")
                    print("="*60)
                    print(text)
                    print("="*60)

                    # Got one, ask if want to continue
                    print("\n[OK] Got transcription! Press Ctrl+C to stop, or continue...")

                else:
                    print("  (No transcription - recording might have been too short)")

            except Exception as e:
                print(f"\n[ERROR in text() call] {e}")
                import traceback
                traceback.print_exc()
                break

        if transcription_count == 0:
            print("\n[!] No transcriptions after 10 attempts")
            print("    - Make sure you're playing audio with speech")
            print("    - Make sure you stop/pause to trigger silence detection")

    except KeyboardInterrupt:
        print("\n\nStopping...")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        if recorder:
            print("Shutting down recorder...")
            try:
                recorder.shutdown()
                print("[OK] Shutdown complete")
            except Exception as e:
                print(f"[WARN] Shutdown error: {e}")
