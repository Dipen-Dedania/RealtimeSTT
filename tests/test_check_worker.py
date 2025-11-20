import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder
import logging
import time

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    print("=" * 60)
    print("WORKER PROCESS CHECK")
    print("=" * 60)

    try:
        print("\n[1] Creating recorder...")
        recorder = AudioToTextRecorder(
            use_loopback=True,
            input_device_index=34,
            silero_sensitivity=0.2,
            webrtc_sensitivity=1,
            spinner=False,
            level=logging.INFO,
        )

        print("[2] Checking worker processes...")

        # Check if transcription worker is alive
        if hasattr(recorder, 'transcript_process'):
            is_alive = recorder.transcript_process.is_alive()
            print(f"    Transcription worker alive: {is_alive}")
            if not is_alive:
                print("    [ERROR] Transcription worker is DEAD!")
                print("    This is why transcription doesn't work!")
        else:
            print("    [ERROR] No transcript_process attribute!")

        # Check if reader worker is alive
        if hasattr(recorder, 'reader_process'):
            is_alive = recorder.reader_process.is_alive()
            print(f"    Audio reader worker alive: {is_alive}")
            if not is_alive:
                print("    [ERROR] Audio reader worker is DEAD!")
        else:
            print("    [ERROR] No reader_process attribute!")

        # Check recording thread
        if hasattr(recorder, 'recording_thread'):
            is_alive = recorder.recording_thread.is_alive()
            print(f"    Recording thread alive: {is_alive}")
            if not is_alive:
                print("    [ERROR] Recording thread is DEAD!")
        else:
            print("    [ERROR] No recording_thread attribute!")

        print("\n[3] Waiting 2 seconds...")
        time.sleep(2)

        print("[4] Checking again...")
        if hasattr(recorder, 'transcript_process'):
            print(f"    Transcription worker still alive: {recorder.transcript_process.is_alive()}")
        if hasattr(recorder, 'reader_process'):
            print(f"    Audio reader worker still alive: {recorder.reader_process.is_alive()}")
        if hasattr(recorder, 'recording_thread'):
            print(f"    Recording thread still alive: {recorder.recording_thread.is_alive()}")

        print("\n[5] Testing if audio queue is working...")
        print("    Waiting 2 seconds for audio chunks...")
        time.sleep(2)
        queue_size = recorder.audio_queue.qsize()
        print(f"    Audio queue size: {queue_size}")
        if queue_size == 0:
            print("    [WARN] No audio chunks in queue - reader might not be working")
        else:
            print("    [OK] Audio chunks are being captured!")

        print("\n[6] Testing transcription pipe...")
        print("    Checking if main_transcription_ready_event is set...")
        if hasattr(recorder, 'main_transcription_ready_event'):
            is_ready = recorder.main_transcription_ready_event.is_set()
            print(f"    Transcription model ready: {is_ready}")
            if not is_ready:
                print("    [ERROR] Transcription model never initialized!")
                print("    This is why transcription hangs!")

        print("\n" + "="*60)
        print("SUMMARY:")
        print("="*60)
        print("If all workers are alive and queue has chunks, the issue is elsewhere.")
        print("If any worker is dead, that's the problem!")
        print("="*60)

        recorder.shutdown()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
