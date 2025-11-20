import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    print("=" * 60)
    print("VERBOSE LOOPBACK TEST - DEVICE 34")
    print("=" * 60)

    # Track all state changes
    def on_vad_detect_start():
        print("\n[1] VAD DETECTION: Started listening for voice")

    def on_vad_start():
        print("[2] VAD: Voice activity DETECTED!")

    def on_recording_start():
        print("[3] RECORDING: Started")

    def on_turn_detection_start():
        print("[4] TURN DETECTION: Waiting for silence...")

    def on_vad_stop():
        print("[5] VAD: Voice activity STOPPED")

    def on_turn_detection_stop():
        print("[6] TURN DETECTION: Voice resumed (reset)")

    def on_recording_stop():
        print("[7] RECORDING: Stopped - now transcribing...")

    def on_transcription_start(audio):
        print(f"[8] TRANSCRIPTION: Starting (audio length: {len(audio)} samples)")

    try:
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=34,

            # More sensitive + shorter silence duration
            silero_sensitivity=0.2,  # Even more sensitive
            webrtc_sensitivity=1,    # Even more sensitive
            post_speech_silence_duration=0.8,  # Shorter wait (was 1.0)
            min_length_of_recording=0.3,  # Minimum recording length

            # All callbacks
            on_vad_detect_start=on_vad_detect_start,
            on_vad_start=on_vad_start,
            on_recording_start=on_recording_start,
            on_turn_detection_start=on_turn_detection_start,
            on_vad_stop=on_vad_stop,
            on_turn_detection_stop=on_turn_detection_stop,
            on_recording_stop=on_recording_stop,
            on_transcription_start=on_transcription_start,

            spinner=False,  # Disable spinner for cleaner output
            level=logging.WARNING,  # Less noise from library
        )

        print("[OK] Recorder initialized!\n")
        print("=" * 60)
        print("INSTRUCTIONS:")
        print("=" * 60)
        print("1. Play a YouTube video with clear SPEECH")
        print("2. Let it play for 2-3 seconds")
        print("3. PAUSE or STOP the video")
        print("4. Wait 1 second - you should see steps [4]-[8]")
        print("5. Watch for transcription output")
        print("=" * 60)
        print("\nWaiting for audio...\n")

        count = 0
        while True:
            print("\n" + "-"*60)
            print("Waiting for speech (Ctrl+C to quit)...")
            print("-"*60)

            text = recorder.text()

            if text:
                count += 1
                print("\n" + "=" * 60)
                print(f"SUCCESS! TRANSCRIPTION #{count}:")
                print("=" * 60)
                print(f"{text}")
                print("=" * 60)
            else:
                print("\n[!] recorder.text() returned empty string")
                print("    This could mean:")
                print("    - Recording was interrupted")
                print("    - Audio was too short")
                print("    - Transcription failed")

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        recorder.shutdown()
        print(f"[OK] Done! Total transcriptions: {count}")

        if count == 0:
            print("\n" + "=" * 60)
            print("TROUBLESHOOTING - NO TRANSCRIPTIONS:")
            print("=" * 60)
            print("Check which step failed:")
            print("  [1-2] Not reached? Audio isn't playing or too quiet")
            print("  [3] Not reached? VAD sensitivity too low")
            print("  [4-7] Not reached? Recording not stopping")
            print("  [8] Reached but no output? Transcription failing")
            print("\nTry:")
            print("  - Increase volume")
            print("  - Use clearer speech (not music)")
            print("  - Wait longer after stopping audio")
            print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        recorder.shutdown()
