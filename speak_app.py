#!/usr/bin/env python3.13
"""
SpeakApp — macOS menu bar TTS app
- Double-tap Caps Lock to stop speaking
- Menu bar icon with voice + speed settings
"""

import rumps
import subprocess
import threading
import time

from AppKit import (NSEvent, NSFlagsChangedMask, NSImage, NSBitmapImageRep,
                    NSPNGFileType, NSGraphicsContext, NSRect, NSZeroRect, NSColor)


def _make_icon(path, size=14):
    sym = NSImage.imageWithSystemSymbolName_accessibilityDescription_("ear", None)
    out = NSImage.alloc().initWithSize_((size, size))
    out.lockFocus()
    ctx = NSGraphicsContext.currentContext()
    ctx.setImageInterpolation_(3)  # NSImageInterpolationHigh
    NSColor.blackColor().set()
    rect = NSRect((0, 0), (size, size))
    sym.drawInRect_(rect)
    out.unlockFocus()
    bmp = NSBitmapImageRep.alloc().initWithData_(out.TIFFRepresentation())
    bmp.representationUsingType_properties_(NSPNGFileType, {}).writeToFile_atomically_(path, True)

VOICES = ["Samantha", "Alex", "Victoria", "Tom", "Ava", "Susan"]
SPEEDS = {"Slow": 140, "Normal": 190, "Fast": 250, "Very Fast": 320}

current_process = None
selected_voice = "Samantha"
selected_speed = 240

caps_event_times = []


def speak(text):
    global current_process
    stop_speaking()
    cmd = ["say", "-v", selected_voice, "-r", str(selected_speed), text]
    current_process = subprocess.Popen(cmd)


def stop_speaking():
    global current_process
    subprocess.run(["pkill", "-x", "say"], capture_output=True)
    if current_process:
        current_process.terminate()
        current_process = None


def handle_flags_event(event):
    global caps_event_times
    flags = event.modifierFlags()
    caps_active = bool(flags & (1 << 16))

    # Count every caps lock state change (on or off)
    now = time.time()
    caps_event_times.append(now)
    caps_event_times[:] = [t for t in caps_event_times if now - t < 0.8]
    if len(caps_event_times) >= 2:
        caps_event_times.clear()
        stop_speaking()


class SpeakApp(rumps.App):
    def __init__(self):
        icon_path = "/Users/eliefrancis/Apps/SpeakApp/icon.png"
        _make_icon(icon_path)
        super().__init__("", icon=icon_path, template=True, quit_button="Quit")
        rumps.Timer(self._resize_icon, 0.3).start()

    def _resize_icon(self, _):
        img = self._nsapp.nsstatusitem.image()
        if img:
            img.setSize_((16, 16))
            self._nsapp.nsstatusitem.setImage_(img)
        self.menu = [
            rumps.MenuItem("Type to Speak...", callback=self.type_to_speak),
            rumps.MenuItem("Stop Speaking", callback=self.stop),
            None,
            rumps.MenuItem("Voice"),
            rumps.MenuItem("Speed"),
            None,
        ]
        self._build_voice_menu()
        self._build_speed_menu()

        # Register global keyboard monitor on main thread after app starts
        rumps.Timer(self._setup_monitor, 0.5).start()

    def _setup_monitor(self, _):
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
            NSFlagsChangedMask, handle_flags_event
        )

    def _build_voice_menu(self):
        voice_menu = rumps.MenuItem("Voice")
        for v in VOICES:
            item = rumps.MenuItem(v, callback=self.set_voice)
            item.state = 1 if v == selected_voice else 0
            voice_menu.add(item)
        self.menu["Voice"] = voice_menu

    def _build_speed_menu(self):
        speed_menu = rumps.MenuItem("Speed")
        for label, val in SPEEDS.items():
            item = rumps.MenuItem(label, callback=self.set_speed)
            item.state = 1 if val == selected_speed else 0
            speed_menu.add(item)
        self.menu["Speed"] = speed_menu

    def type_to_speak(self, _):
        response = rumps.Window(
            message="Type something to speak:",
            title="Type to Speak",
            ok="Speak",
            cancel="Cancel",
            dimensions=(400, 60),
        ).run()
        if response.clicked and response.text.strip():
            threading.Thread(target=speak, args=(response.text,), daemon=True).start()

    def stop(self, _):
        stop_speaking()

    def set_voice(self, sender):
        global selected_voice
        selected_voice = sender.title
        for v in VOICES:
            self.menu["Voice"][v].state = 1 if v == selected_voice else 0

    def set_speed(self, sender):
        global selected_speed
        selected_speed = SPEEDS[sender.title]
        for label in SPEEDS:
            self.menu["Speed"][label].state = 1 if label == sender.title else 0


if __name__ == "__main__":
    SpeakApp().run()
