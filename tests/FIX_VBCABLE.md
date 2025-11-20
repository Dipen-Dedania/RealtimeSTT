# How to Fix VB-Cable Audio Routing (Device 38)

## Problem
Device 38 shows amplitude of 1 (no audio). This means no audio is being routed to VB-Cable.

## Solution: Route Audio to VB-Cable

### Option 1: Windows Sound Settings (Per-Application)

**For specific apps (Chrome, Zoom, etc.):**

1. Open **Settings** → **System** → **Sound**
2. Scroll down to **Advanced sound options**
3. Click **App volume and device preferences**
4. Find your application (e.g., Chrome, Spotify)
5. Change **Output** to: **CABLE Input (VB-Audio Virtual Cable)**
6. Keep your speaker output on default

This routes only that app's audio through VB-Cable.

### Option 2: Set VB-Cable as Default Output (System-wide)

**Routes ALL system audio:**

1. Right-click the speaker icon in taskbar
2. Select **Open Sound settings**
3. Under **Output**, select: **CABLE Input (VB-Audio Virtual Cable)**
4. Play audio - it will now go through VB-Cable

**Important:** You won't hear the audio unless you also:
- Set VB-Cable as a "Listen to this device" in Recording devices, OR
- Use software that monitors VB-Cable output

### Option 3: Use VB-Cable "Listen" Feature (Recommended)

This lets you both hear the audio AND capture it:

1. Right-click speaker icon → **Sounds**
2. Go to **Recording** tab
3. Find **CABLE Output**
4. Right-click → **Properties**
5. Go to **Listen** tab
6. Check **Listen to this device**
7. Select your speakers/headphones in the dropdown
8. Click **Apply**

Now audio routed to CABLE Input will play through your speakers too!

## Verify It's Working

Run the diagnostic again:
```bash
python tests/diagnose_loopback_auto.py
```

While it's running, play a YouTube video. You should see amplitude values > 1000.

## Still Not Working?

### Check VB-Cable Installation
- Download from: https://vb-audio.com/Cable/
- Install and restart computer
- Verify device 38 exists (you already confirmed this)

### Use Device 34 Instead (Much Easier!)
Device 34 captures your speaker output directly - no routing needed!

```bash
python tests/test_device_34_audio.py
```

This is the simplest solution for most use cases.
