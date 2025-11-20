"""
List all available audio devices including loopback devices
"""
try:
    import pyaudiowpatch as pyaudio
    print("Using pyaudiowpatch (loopback support enabled)")
except ImportError:
    import pyaudio
    print("Using standard pyaudio (no loopback support)")

print("=" * 70)
print("AVAILABLE AUDIO DEVICES")
print("=" * 70)

p = pyaudio.PyAudio()

# Try to get default loopback device
try:
    default_loopback = p.get_default_wasapi_loopback()
    print(f"\n[DEFAULT LOOPBACK DEVICE]")
    print(f"  Index: {default_loopback['index']}")
    print(f"  Name: {default_loopback['name']}")
    print(f"  Channels: {default_loopback['maxInputChannels']}")
    print(f"  Sample Rate: {int(default_loopback['defaultSampleRate'])} Hz")
except (OSError, AttributeError) as e:
    print(f"\n[NO DEFAULT LOOPBACK] {e}")

print("\n" + "=" * 70)
print("ALL DEVICES:")
print("=" * 70)

for i in range(p.get_device_count()):
    try:
        info = p.get_device_info_by_index(i)
        device_type = []

        if info['maxInputChannels'] > 0:
            device_type.append("INPUT")
        if info['maxOutputChannels'] > 0:
            device_type.append("OUTPUT")

        # Check if it's a loopback device
        is_loopback = "loopback" in info['name'].lower()
        if is_loopback:
            device_type.append("LOOPBACK")

        type_str = " | ".join(device_type) if device_type else "UNKNOWN"

        print(f"\n[Device {i}] {type_str}")
        print(f"  Name: {info['name']}")
        print(f"  Input Channels: {info['maxInputChannels']}")
        print(f"  Output Channels: {info['maxOutputChannels']}")
        print(f"  Default Sample Rate: {int(info['defaultSampleRate'])} Hz")

        if is_loopback:
            print(f"  >>> THIS IS A LOOPBACK DEVICE <<<")

    except Exception as e:
        print(f"\n[Device {i}] ERROR: {e}")

p.terminate()

print("\n" + "=" * 70)
print("NOTES:")
print("=" * 70)
print("- LOOPBACK devices capture system audio output")
print("- Loopback only works with SPEAKERS, not headphones")
print("- For headphones, you need virtual audio cable software")
print("=" * 70)
