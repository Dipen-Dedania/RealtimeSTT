import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RealtimeSTT import AudioToTextRecorder

def process_text(text):
    print(f"Transcription: {text}")

if __name__ == '__main__':
    print("Starting loopback recording test...")
    print("Please play some audio on your system (e.g., a YouTube video).")
    
    # Initialize recorder with use_loopback=True
    # We assume the default loopback device will be found
    try:
        recorder = AudioToTextRecorder(
            model="tiny", # Use tiny model for fast testing
            use_loopback=True,
            spinner=True,
            debug_mode=True
        )
        
        print("Recorder initialized. Recording for 10 seconds...")
        
        start_time = time.time()
        while time.time() - start_time < 10:
            recorder.text(process_text)
            
        print("Stopping recorder...")
        recorder.shutdown()
        print("Test finished.")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
