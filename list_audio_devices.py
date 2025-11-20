import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    
    wasapi_index = None
    output = []
    output.append("Host APIs:")
    for i in range(p.get_host_api_count()):
        api_info = p.get_host_api_info_by_index(i)
        output.append(f"  {i}: {api_info['name']}")
        if "WASAPI" in api_info['name']:
            wasapi_index = i

    if wasapi_index is None:
        output.append("WASAPI Host API not found.")
        with open("devices.txt", "w") as f:
            f.write("\n".join(output))
        p.terminate()
        return

    output.append(f"\nWASAPI Devices (Host API Index {wasapi_index}):")
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if dev_info['hostApi'] == wasapi_index:
            output.append(f"  Device {i}: {dev_info['name']}")
            output.append(f"    Max Input Channels: {dev_info['maxInputChannels']}")
            output.append(f"    Max Output Channels: {dev_info['maxOutputChannels']}")
            output.append(f"    Default Sample Rate: {dev_info['defaultSampleRate']}")
            output.append("-" * 30)

    with open("devices.txt", "w") as f:
        f.write("\n".join(output))

    p.terminate()

if __name__ == "__main__":
    list_audio_devices()
