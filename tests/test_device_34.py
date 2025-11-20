import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging

# Enable logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    print("=" * 60)
    print("LOOPBACK TEST - DEVICE 34 (HEADPHONES)")
    print("=" * 60)
    print("\nThis captures audio playing through your speakers/headphones")
    print("No VB-Cable configuration needed!\n")

    # Callbacks for debugging
    def on_vad_start():
        print("\n[VAD] Voice activity STARTED")

    def on_recording_start():
        print("[RECORDING] Started recording")

    def on_recording_stop():
        print("[RECORDING] Stopped recording\n")

    try:
        # Use device 34 - Headphones Loopback
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=34,  # Headphones (High Definition Audio Device) [Loopback]

            # More sensitive settings for loopback
            silero_sensitivity=0.3,
            webrtc_sensitivity=2,
            post_speech_silence_duration=1.0,

            # Callbacks
            on_vad_start=on_vad_start,
            on_recording_start=on_recording_start,
            on_recording_stop=on_recording_stop,

            spinner=True,
            level=logging.INFO,
        )

        print("[OK] Recorder initialized!")
        print("\n" + "=" * 60)
        print("INSTRUCTIONS:")
        print("=" * 60)
        print("1. Play a YouTube video with SPEECH (not just music)")
        print("2. Make sure volume is at reasonable level (not muted!)")
        print("3. Watch for [VAD] messages")
        print("4. Press Ctrl+C to stop")
        print("=" * 60)
        print("\nListening...\n")

        count = 0
        while True:
            text = recorder.text()
            if text:
                count += 1
                print("=" * 60)
                print(f"TRANSCRIPTION #{count}: {text}")
                print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        recorder.shutdown()
        print("[OK] Done!")

        if count == 0:
            print("\n[!] No transcriptions - try increasing volume or using clearer speech audio")
