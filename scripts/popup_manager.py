#!/usr/bin/env python3
"""
Popup Lifecycle & Toggle Manager for Niri Panel
Ensures exclusive popup display, singleton execution, and smooth toggling.
"""

import json
import os
import signal
import subprocess
import sys
from pathlib import Path

RUN_DIR = Path("/tmp/niri-panel-popups")
STATE_FILE = RUN_DIR / "active_popup.json"

POPUP_MAP = {
    "clock": "popup/clock/clock_popup.py",
    "audio": "popup/audio/audio_popup.py",
    "battery": "popup/battery/battery_popup.py",
    "power": "popup/battery/battery_popup.py",
    "bluetooth": "popup/bluetooth/bluetooth_popup.py",
    "storage": "popup/storage/storage_popup.py",
    "disk": "popup/storage/storage_popup.py",
    "keyboard": "popup/keyboard/keyboard_popup.py",
    "tray": "popup/tray/tray_popup.py",
    "window_menu": "popup/taskbar/window_menu.py",
    "context_menu": "popup/taskbar/context_menu.py"
}

def ensure_dir():
    RUN_DIR.mkdir(parents=True, exist_ok=True)

def get_active_popup():
    ensure_dir()
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            pid = data.get("pid")
            name = data.get("name")
            if pid and os.path.exists(f"/proc/{pid}"):
                return name, pid
        except Exception:
            pass
    return None, None

def close_active():
    name, pid = get_active_popup()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except Exception:
            pass
    if STATE_FILE.exists():
        try:
            STATE_FILE.unlink()
        except Exception:
            pass
    return name

def open_popup(name, extra_args=None):
    close_active()
    rel_path = POPUP_MAP.get(name)
    if not rel_path:
        print(f"Unknown popup: {name}")
        return

    # Check installed path vs repository path
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    
    popup_script = base_dir / rel_path
    if not popup_script.exists():
        # Check ~/.config/niri-panel
        alt_path = Path.home() / ".config" / "niri-panel" / rel_path
        if alt_path.exists():
            popup_script = alt_path

    if not popup_script.exists():
        print(f"Popup script not found: {rel_path}")
        return

    cmd = [sys.executable, str(popup_script)]
    if extra_args:
        cmd.extend(extra_args)

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Save state
    ensure_dir()
    STATE_FILE.write_text(json.dumps({
        "name": name,
        "pid": proc.pid
    }))

def toggle_popup(name, extra_args=None):
    active_name, active_pid = get_active_popup()
    if active_name == name:
        close_active()
    else:
        open_popup(name, extra_args)

def main():
    if len(sys.argv) < 2:
        print("Usage: popup_manager.py [toggle|open|close|close-all] <popup_name> [args...]")
        sys.exit(1)

    action = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else ""
    extra = sys.argv[3:] if len(sys.argv) > 3 else None

    if action == "toggle":
        toggle_popup(name, extra)
    elif action == "open":
        open_popup(name, extra)
    elif action == "close":
        close_active()
    elif action == "close-all":
        close_active()
    else:
        toggle_popup(action)

if __name__ == "__main__":
    main()
