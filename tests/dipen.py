import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    print("=" * 60)
    print("LOOPBACK AUDIO TRANSCRIPTION TEST")
    print("=" * 60)
    print("\nInitializing recorder with loopback audio capture...")
    print("This will transcribe system audio (speakers/YouTube/meetings)\n")

    # Initialize with use_loopback=True to capture system audio
    # Use device 38 (CABLE Input Loopback) to capture audio routed through VB-Cable
    recorder = AudioToTextRecorder(
        use_loopback=True,
        input_device_index=38,  # CABLE Input (VB-Audio Virtual Cable) [Loopback]
        spinner=True,
        # model="base",  # You can use a bigger model for better accuracy
    )

    print("[OK] Recorder initialized successfully!")
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print("1. In your meeting app (Teams/Zoom), set audio output to:")
    print("   'CABLE Input (VB-Audio Virtual Cable)'")
    print("2. OR play YouTube video with audio output set to CABLE Input")
    print("3. OR simply unplug headphones to use speakers (simplest)")
    print("4. The system will detect voice and start transcribing")
    print("5. Press Ctrl+C to stop\n")
    print("=" * 60)
    print("Listening for audio from VB-Cable (Device 38)...\n")

    try:
        while True:
            # Use synchronous approach (simpler and more reliable)
            text = recorder.text()

            if text:
                print("=" * 60)
                print(f"TRANSCRIPTION: {text}")
                print("=" * 60)
                print()

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        recorder.shutdown()
        print("[OK] Shutdown complete!")
