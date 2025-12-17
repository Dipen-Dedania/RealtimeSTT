"""
Realtime transcription for Electron/Node.js integration
Uses the RealtimeSTT library for proper text stabilization
Communicates via JSON over stdin/stdout
"""
import sys
import os
import json
import threading
import time

# Import RealtimeSTT directly from the module
from RealtimeSTT.audio_recorder import AudioToTextRecorder

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    try:
        import pyaudio
    except:
        pyaudio = None


class ElectronTranscriber:
    def __init__(self):
        self.recorder = None
        self.running = False
        self.transcribe_thread = None

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
        """Initialize RealtimeSTT recorder"""
        try:
            self.send_message("status", {"message": "Loading models..."})

            # Define callbacks for RealtimeSTT - must be passed to constructor
            def on_recording_start():
                self.send_message("speech_detected", {"message": "Speech started"})

            def on_recording_stop():
                pass  # Speech ended, RealtimeSTT will send final transcription

            def on_realtime_transcription_update(text):
                # Partial/realtime update
                self.send_message("transcription", {
                    "text": text,
                    "is_partial": True,
                    "is_stable": False
                })

            def on_realtime_transcription_stabilized(text):
                # Stabilized text (RealtimeSTT's sophisticated logic determined this is stable)
                self.send_message("transcription", {
                    "text": text,
                    "is_partial": False,
                    "is_stable": True
                })

            # Initialize AudioToTextRecorder with proper settings
            self.recorder = AudioToTextRecorder(
                model=model,
                language="en",

                # Use specified device (loopback)
                use_loopback=True,
                input_device_index=device_index,

                # Realtime processing settings
                silero_sensitivity=0.4,
                webrtc_sensitivity=3,
                post_speech_silence_duration=0.4,
                min_length_of_recording=1.0,
                min_gap_between_recordings=0,

                # Enable features
                enable_realtime_transcription=True,
                realtime_processing_pause=0.1,

                # Callbacks - must be passed to constructor
                on_recording_start=on_recording_start,
                on_recording_stop=on_recording_stop,
                on_realtime_transcription_update=on_realtime_transcription_update,
                on_realtime_transcription_stabilized=on_realtime_transcription_stabilized,

                # Processing settings
                beam_size=3,

                # Disable unnecessary features for speed
                spinner=False,
                level=0  # Disable logging
            )

            self.send_message("status", {"message": "Opening audio stream..."})
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

            if not self.recorder:
                raise Exception("Recorder not initialized. Call initialize() first.")

            self.running = True

            # Start transcription in a thread
            self.transcribe_thread = threading.Thread(target=self._transcribe_loop, daemon=True)
            self.transcribe_thread.start()

            self.send_message("started", {"message": "Transcription started"})

        except Exception as e:
            self.send_message("error", {"message": str(e)})

    def stop(self):
        """Stop transcription"""
        try:
            self.running = False

            if self.recorder:
                self.recorder.stop()
                self.recorder.shutdown()

            self.send_message("stopped", {"message": "Transcription stopped"})

        except Exception as e:
            self.send_message("error", {"message": str(e)})

    def _transcribe_loop(self):
        """Main transcription loop using RealtimeSTT callbacks"""
        try:
            # Start recording - callbacks were set in constructor
            while self.running:
                try:
                    # text() blocks until speech segment is complete
                    # Realtime callbacks fire during this time
                    text = self.recorder.text()

                    # Send final transcription for this speech segment
                    if text:
                        self.send_message("transcription", {
                            "text": text,
                            "is_partial": False,
                            "is_stable": True,
                            "is_final": True
                        })

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if self.running:
                        self.send_message("error", {"message": f"Transcription error: {str(e)}"})
                        time.sleep(0.5)

        except Exception as e:
            self.send_message("error", {"message": f"Transcription loop error: {str(e)}"})

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
    import multiprocessing
    multiprocessing.freeze_support()
    main()
