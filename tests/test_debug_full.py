import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging

# Enable ALL debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    print("=" * 60)
    print("FULL DEBUG TEST")
    print("=" * 60)
    print("This will show ALL internal logs\n")

    def on_recording_stop():
        print("\n>>> [USER] Recording stopped - transcribing...")

    try:
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=34,

            # Very sensitive
            silero_sensitivity=0.1,
            webrtc_sensitivity=0,
            post_speech_silence_duration=0.5,
            min_length_of_recording=0.3,

            on_recording_stop=on_recording_stop,

            spinner=False,
            level=logging.DEBUG,  # Full debug from library
        )

        print("\n[OK] Recorder ready with FULL DEBUG logging")
        print("Play speech for 2-3 seconds, then stop\n")

        count = 0
        while count < 1:  # Just get one transcription
            print("\n" + "="*60)
            print("Waiting for speech...")
            print("="*60 + "\n")

            text = recorder.text()

            if text:
                count += 1
                print(f"\n{'='*60}")
                print(f"SUCCESS! TRANSCRIPTION:")
                print(f"{'='*60}")
                print(f"{text}")
                print(f"{'='*60}\n")
            else:
                print("\n[!] Got empty string from recorder.text()")

        print("\nGot one transcription, shutting down...")
        recorder.shutdown()
        print("Done!")

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        recorder.shutdown()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        recorder.shutdown()
