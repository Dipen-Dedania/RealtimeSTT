import pyaudiowpatch as pyaudio
import wave

# Configuration
OUTPUT_FILENAME = "loopback_test.wav"
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2 # Loopback is usually stereo
RATE = 48000 # Match the device default sample rate from devices.txt
RECORD_SECONDS = 5
# Device 24 is "Headphones (High Definition Audio Device)" which is an output device.
# We want to record from it in loopback mode.
DEVICE_INDEX = 24 

def record_loopback():
    p = pyaudio.PyAudio()

    print(f"Attempting to record from device {DEVICE_INDEX} with loopback...")

    try:
        # Open the stream with as_loopback=True
        # Note: channels must match the device's output channels (usually 2 for speakers/headphones)
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=DEVICE_INDEX,
                        frames_per_buffer=CHUNK_SIZE,
                        as_loopback=True)

        print("Recording started...")
        frames = []

        for i in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)):
            data = stream.read(CHUNK_SIZE)
            frames.append(data)

        print("Recording finished.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Saved to {OUTPUT_FILENAME}")

    except Exception as e:
        print(f"Error: {e}")
        p.terminate()

if __name__ == "__main__":
    record_loopback()
