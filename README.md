# SpeakApp

macOS menu bar TTS app with double-tap Caps Lock to stop speech.

## Features
- **Type to Speak** — click the menu bar icon, type text, hit Speak
- **Start Dictation** — triggers macOS built-in dictation
- **Stop Speaking** — menu button to stop
- **Double-tap Caps Lock** — stop speech instantly from anywhere
- **Voice selector** — Samantha, Alex, Victoria, Tom, Ava, Susan
- **Speed selector** — Slow, Normal, Fast, Very Fast
- Auto-starts on login

## Install

```bash
pip3 install rumps pynput pyobjc-framework-Quartz pyobjc-framework-Cocoa --break-system-packages
python3 speak_app.py
```

## Troubleshooting

### Double-tap Caps Lock not stopping speech

macOS caps lock has a built-in hardware debounce delay (~150ms). If double-tapping isn't registering, the detection window may be too short.

**Fix:** In `speak_app.py`, increase the detection window:

```python
# Default is 1.5 seconds — increase if double-tap isn't registering
caps_event_times[:] = [t for t in caps_event_times if now - t < 1.5]
```

Also check **System Settings > Accessibility > Keyboard** and make sure **Slow Keys** is turned off — that adds an extra delay to all key presses.

### Speech stops randomly while typing

This was a bug where modifier keys (Shift, Command, Option) were being counted as caps lock events. Fixed in v2 — make sure you're on the latest version.
