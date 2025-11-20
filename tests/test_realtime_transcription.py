import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging

logging.basicConfig(level=logging.WARNING)

if __name__ == '__main__':
    print("=" * 60)
    print("REALTIME TRANSCRIPTION TEST (CONTINUOUS)")
    print("=" * 60)
    print("\nThis will transcribe WHILE audio is playing!")
    print("No need to wait for silence.\n")

    current_text = ""

    def on_realtime_update(text):
        """Called frequently with partial transcription"""
        global current_text
        # Clear line and print
        print(f"\r[REALTIME] {text}", end="", flush=True)
        current_text = text

    def on_realtime_stabilized(text):
        """Called when transcription stabilizes (more reliable)"""
        print(f"\n[STABLE] {text}")

    def on_recording_start():
        print("\n>>> Recording started - transcribing in real-time...\n")

    def on_recording_stop():
        global current_text
        print("\n>>> Recording stopped")
        current_text = ""

    try:
        print("[1] Initializing recorder with realtime transcription...")
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=34,

            # Enable realtime transcription
            enable_realtime_transcription=True,
            realtime_processing_pause=0.2,  # Update every 0.2 seconds
            realtime_model_type="tiny",  # Fast model for realtime

            # Callbacks for realtime updates
            on_realtime_transcription_update=on_realtime_update,
            on_realtime_transcription_stabilized=on_realtime_stabilized,
            on_recording_start=on_recording_start,
            on_recording_stop=on_recording_stop,

            # More sensitive VAD
            silero_sensitivity=0.2,
            webrtc_sensitivity=1,

            # Don't stop on short silences
            post_speech_silence_duration=2.0,  # Wait 2 seconds before stopping

            spinner=False,
            level=logging.WARNING,
        )

        print("[2] Recorder ready!\n")
        print("=" * 60)
        print("INSTRUCTIONS:")
        print("=" * 60)
        print("1. Play a YouTube video with continuous speech")
        print("2. Watch the realtime transcription appear as it speaks!")
        print("3. Press Ctrl+C to stop")
        print("=" * 60)
        print("\nListening...\n")

        # Just keep the recorder running
        # Realtime callbacks will handle the transcription
        while True:
            try:
                # This will block until recording stops (after silence)
                # But realtime callbacks fire during recording!
                final_text = recorder.text()

                if final_text:
                    print("\n\n" + "=" * 60)
                    print("FINAL TRANSCRIPTION:")
                    print("=" * 60)
                    print(final_text)
                    print("=" * 60)
                    print("\nListening for more...\n")

            except Exception as e:
                print(f"\n[ERROR in text()] {e}")
                break

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        recorder.shutdown()
        print("[OK] Done!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        try:
            recorder.shutdown()
        except:
            pass
