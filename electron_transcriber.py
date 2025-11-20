"""
Realtime transcription for Electron/Node.js integration
Communicates via JSON over stdin/stdout
"""
import sys
import os
import json
import threading
import time
from collections import deque

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    try:
        import pyaudio
    except:
        pyaudio = None

import numpy as np
from faster_whisper import WhisperModel
import webrtcvad

# Use numpy-based resampling to avoid scipy PyInstaller issues
def resample(data, num_samples):
    """
    Resample audio data using numpy interpolation (replaces scipy.signal.resample)
    This is a simple but effective alternative that works with PyInstaller.
    """
    if len(data) == num_samples:
        return data

    # Create interpolation points
    x_old = np.linspace(0, 1, len(data))
    x_new = np.linspace(0, 1, num_samples)

    # Use numpy's interp for 1D linear interpolation
    resampled = np.interp(x_new, x_old, data)

    return resampled.astype(data.dtype)


class ElectronTranscriber:
    def __init__(self):
        self.whisper_model = None
        self.vad = None
        self.p = None
        self.stream = None
        self.frames = deque(maxlen=500)
        self.recording = False
        self.running = False
        self.last_transcribe = time.time()
        self.audio_thread = None
        self.transcribe_thread = None
        self.device_index = None
        
    def send_message(self, message_type, data):
        """Send JSON message to stdout for Node.js to read"""
        message = {
            "type": message_type,
            "data": data,
            "timestamp": time.time()
        }
        # Write to stdout and flush immediately
        print(json.dumps(message), flush=True)
    
    def initialize(self, device_index=34, model="tiny"):
        """Initialize models and audio stream"""
        try:
            self.send_message("status", {"message": "Loading models..."})
            
            # Load Whisper model
            self.whisper_model = WhisperModel(model, device="cpu", compute_type="int8")
            self.vad = webrtcvad.Vad(1)
            
            self.send_message("status", {"message": "Opening audio stream..."})
            
            # Open audio stream
            self.p = pyaudio.PyAudio()
            self.device_index = device_index
            
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=2,
                rate=48000,
                input=True,
                frames_per_buffer=1024,
                input_device_index=device_index,
            )
            
            self.send_message("initialized", {"device": device_index, "model": model})
            
        except Exception as e:
            self.send_message("error", {"message": str(e)})
            raise
    
    def start(self):
        """Start transcription"""
        try:
            if self.running:
                self.send_message("warning", {"message": "Already running"})
                return
            
            self.running = True
            
            # Start audio capture thread
            self.audio_thread = threading.Thread(target=self._capture_audio, daemon=True)
            self.audio_thread.start()
            
            # Start transcription thread
            self.transcribe_thread = threading.Thread(target=self._realtime_transcribe, daemon=True)
            self.transcribe_thread.start()
            
            self.send_message("started", {"message": "Transcription started"})
            
        except Exception as e:
            self.send_message("error", {"message": str(e)})
    
    def stop(self):
        """Stop transcription"""
        try:
            self.running = False
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            
            if self.p:
                self.p.terminate()
            
            self.send_message("stopped", {"message": "Transcription stopped"})
            
        except Exception as e:
            self.send_message("error", {"message": str(e)})
    
    def _capture_audio(self):
        """Continuously capture audio"""
        while self.running:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.int16)
                
                # Check for speech with VAD
                audio_mono = audio_np.reshape(-1, 2).mean(axis=1).astype(np.int16)
                audio_16k = resample(audio_mono, int(len(audio_mono) * 16000 / 48000))
                audio_16k_bytes = audio_16k.astype(np.int16).tobytes()
                
                is_speech = False
                frame_length = int(16000 * 0.01)
                for i in range(len(audio_16k_bytes) // (2 * frame_length)):
                    frame = audio_16k_bytes[i*frame_length*2:(i+1)*frame_length*2]
                    if len(frame) == frame_length * 2:
                        try:
                            if self.vad.is_speech(frame, 16000):
                                is_speech = True
                                break
                        except:
                            pass
                
                if is_speech:
                    if not self.recording:
                        self.send_message("speech_detected", {"message": "Speech started"})
                        self.recording = True
                        self.frames.clear()
                    
                    self.frames.append(data)
                elif self.recording:
                    # Keep adding for a bit after speech stops
                    self.frames.append(data)
                
            except Exception as e:
                self.send_message("error", {"message": f"Capture error: {str(e)}"})
                break
    
    def _realtime_transcribe(self):
        """Transcribe every 0.5 seconds while recording"""
        while self.running:
            try:
                if self.recording and len(self.frames) > 20:
                    now = time.time()
                    
                    # Transcribe every 0.5 seconds
                    if now - self.last_transcribe >= 0.5:
                        self.last_transcribe = now
                        
                        # Get current audio
                        all_audio = np.frombuffer(b''.join(self.frames), dtype=np.int16)
                        audio_mono = all_audio.reshape(-1, 2).mean(axis=1)
                        
                        # Resample to 16kHz
                        audio_16k = resample(audio_mono, int(len(audio_mono) * 16000 / 48000))
                        audio_float = audio_16k.astype(np.float32) / 32768.0
                        
                        # Transcribe
                        segments, info = self.whisper_model.transcribe(
                            audio_float,
                            language="en",
                            beam_size=3,
                            vad_filter=False
                        )
                        text = " ".join(seg.text for seg in segments).strip()
                        
                        if text:
                            self.send_message("transcription", {
                                "text": text,
                                "is_partial": True
                            })
                
                time.sleep(0.1)
                
            except Exception as e:
                self.send_message("error", {"message": f"Transcription error: {str(e)}"})
                time.sleep(0.5)
    
    def list_devices(self):
        """List available audio devices"""
        try:
            p = pyaudio.PyAudio()
            devices = []
            
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                devices.append({
                    "index": i,
                    "name": info.get("name"),
                    "channels": info.get("maxInputChannels"),
                    "sampleRate": int(info.get("defaultSampleRate"))
                })
            
            p.terminate()
            self.send_message("devices", {"devices": devices})
            
        except Exception as e:
            self.send_message("error", {"message": str(e)})


def main():
    transcriber = ElectronTranscriber()
    
    # Send ready message
    transcriber.send_message("ready", {"message": "Transcriber ready"})
    
    # Listen for commands from Node.js via stdin
    try:
        for line in sys.stdin:
            try:
                command = json.loads(line.strip())
                cmd_type = command.get("command")
                
                if cmd_type == "initialize":
                    device_index = command.get("deviceIndex", 34)
                    model = command.get("model", "tiny")
                    transcriber.initialize(device_index, model)
                
                elif cmd_type == "start":
                    transcriber.start()
                
                elif cmd_type == "stop":
                    transcriber.stop()
                
                elif cmd_type == "list_devices":
                    transcriber.list_devices()
                
                elif cmd_type == "exit":
                    transcriber.stop()
                    break
                
                else:
                    transcriber.send_message("error", {"message": f"Unknown command: {cmd_type}"})
                    
            except json.JSONDecodeError as e:
                transcriber.send_message("error", {"message": f"Invalid JSON: {str(e)}"})
            except Exception as e:
                transcriber.send_message("error", {"message": str(e)})
    
    except KeyboardInterrupt:
        transcriber.stop()


if __name__ == '__main__':
    main()
