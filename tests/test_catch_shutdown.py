import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging
import time

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    print("=" * 60)
    print("CATCH SHUTDOWN CAUSE TEST")
    print("=" * 60)

    try:
        print("\n[1] Creating recorder...")
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=34,
            silero_sensitivity=0.2,
            webrtc_sensitivity=1,
            spinner=False,
            level=logging.DEBUG,
        )

        print("\n[2] Recorder created, checking state...")
        print(f"    is_shut_down: {recorder.is_shut_down}")
        print(f"    shutdown_event set: {recorder.shutdown_event.is_set()}")
        print(f"    interrupt_stop_event set: {recorder.interrupt_stop_event.is_set()}")

        print("\n[3] Checking worker processes...")
        if hasattr(recorder, 'transcript_process'):
            print(f"    transcript_process alive: {recorder.transcript_process.is_alive()}")
        if hasattr(recorder, 'reader_process'):
            print(f"    reader_process alive: {recorder.reader_process.is_alive()}")

        print("\n[4] Waiting 1 second...")
        time.sleep(1)

        print("\n[5] Checking again...")
        print(f"    is_shut_down: {recorder.is_shut_down}")
        print(f"    shutdown_event set: {recorder.shutdown_event.is_set()}")
        print(f"    interrupt_stop_event set: {recorder.interrupt_stop_event.is_set()}")
        if hasattr(recorder, 'transcript_process'):
            print(f"    transcript_process alive: {recorder.transcript_process.is_alive()}")
        if hasattr(recorder, 'reader_process'):
            print(f"    reader_process alive: {recorder.reader_process.is_alive()}")

        print("\n[6] Calling recorder.text()...")
        print("    (This is where it usually shuts down)")

        # Call text() and catch any exceptions
        try:
            text = recorder.text()
            print(f"\n[7] recorder.text() returned: '{text}'")
        except KeyboardInterrupt:
            print("\n[7] KeyboardInterrupt caught!")
        except Exception as e:
            print(f"\n[7] Exception caught: {e}")
            import traceback
            traceback.print_exc()

        print("\n[8] After text() call, checking state...")
        print(f"    is_shut_down: {recorder.is_shut_down}")
        print(f"    shutdown_event set: {recorder.shutdown_event.is_set()}")

        print("\n[9] Manually shutting down...")
        recorder.shutdown()
        print("[OK] Done")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
