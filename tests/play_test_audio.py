"""
Simple script to play text-to-speech audio for testing loopback transcription.
Run this WHILE the loopback test (dipen.py) is running in another terminal.
"""
import pyttsx3
import time

print("=" * 60)
print("AUDIO PLAYBACK TEST")
print("=" * 60)
print("\nMake sure tests/dipen.py is running in another terminal!")
print("This will speak some text that should be transcribed.\n")

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed
engine.setProperty('volume', 0.9)  # Volume

test_phrases = [
    "Hello, this is a test of the loopback audio transcription system.",
    "If you can see this text transcribed, the system is working correctly.",
    "Thank you for testing the real-time speech to text functionality."
]

print("Speaking in 3 seconds...\n")
time.sleep(3)

for i, phrase in enumerate(test_phrases, 1):
    print(f"[{i}/{len(test_phrases)}] Speaking: {phrase}")
    engine.say(phrase)
    engine.runAndWait()
    time.sleep(2)

print("\n[OK] Audio playback complete!")
print("Check the other terminal for transcriptions.")
