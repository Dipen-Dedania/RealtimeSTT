import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging

# Enable more detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    print("=" * 60)
    print("LOOPBACK AUDIO TRANSCRIPTION TEST (DEBUG MODE)")
    print("=" * 60)
    print("\nInitializing recorder with loopback audio capture...")
    print("This will transcribe system audio (speakers/YouTube/meetings)\n")

    # Callback to see when VAD detects voice
    def on_vad_start():
        print("\n[VAD] Voice activity STARTED")

    def on_vad_stop():
        print("[VAD] Voice activity STOPPED\n")

    def on_recording_start():
        print("\n[RECORDING] Started recording")

    def on_recording_stop():
        print("[RECORDING] Stopped recording\n")

    try:
        # Initialize with adjusted settings for loopback audio
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=38,  # CABLE Input (VB-Audio Virtual Cable) [Loopback]

            # ADJUSTED VAD SETTINGS FOR LOOPBACK
            silero_sensitivity=0.3,      # Lower = more sensitive (default: 0.4)
            webrtc_sensitivity=2,        # Lower = more sensitive (default: 3)
            post_speech_silence_duration=1.0,  # Wait 1 second of silence before stopping

            # Callbacks for debugging
            on_vad_start=on_vad_start,
            on_vad_stop=on_vad_stop,
            on_recording_start=on_recording_start,
            on_recording_stop=on_recording_stop,

            # Other settings
            spinner=True,
            level=logging.INFO,  # Show important messages
            # model="base",  # Use a bigger model for better accuracy
        )

        print("[OK] Recorder initialized successfully!")
        print("\n" + "=" * 60)
        print("INSTRUCTIONS:")
        print("=" * 60)
        print("1. PLAY AUDIO NOW (YouTube video, meeting audio, etc.)")
        print("2. Make sure audio output is set to:")
        print("   'CABLE Input (VB-Audio Virtual Cable)'")
        print("3. OR simply use your default speakers (Device 34)")
        print("4. Watch for [VAD] messages to see if voice is detected")
        print("5. Press Ctrl+C to stop\n")
        print("=" * 60)
        print("Listening for audio from device 38...")
        print("(If no [VAD] messages appear, audio is not being detected)\n")

        transcription_count = 0

        while True:
            # Use synchronous approach (simpler and more reliable)
            text = recorder.text()

            if text:
                transcription_count += 1
                print("=" * 60)
                print(f"TRANSCRIPTION #{transcription_count}: {text}")
                print("=" * 60)
                print()

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        recorder.shutdown()
        print("[OK] Shutdown complete!")

        if transcription_count == 0:
            print("\n" + "=" * 60)
            print("[!] NO TRANSCRIPTIONS OCCURRED!")
            print("=" * 60)
            print("\nTroubleshooting checklist:")
            print("  [ ] Was audio actually playing?")
            print("  [ ] Did you see any [VAD] messages?")
            print("  [ ] Is audio routed to CABLE Input?")
            print("\nNext steps:")
            print("  1. Run: python tests/diagnose_loopback_auto.py")
            print("  2. Try device 34 (Headphones Loopback) instead")
            print("  3. Lower silero_sensitivity to 0.2")
            print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        recorder.shutdown()
