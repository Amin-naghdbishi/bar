#!/usr/bin/env python3
"""
Clean Bluetooth Status for Waybar
- Bluetooth icon ONLY
- Dynamic icon based on power and connection state
- No tooltips (clicking opens the real Bluetooth Center popup window)
"""

import json
import subprocess
import sys

def get_bluetooth_info():
    powered = False
    has_connected = False

    try:
        proc = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True, timeout=1)
        if proc.returncode == 0 and "Powered: yes" in proc.stdout:
            powered = True

        if powered:
            proc_dev = subprocess.run(["bluetoothctl", "devices", "Connected"], capture_output=True, text=True, timeout=1)
            if proc_dev.returncode == 0 and proc_dev.stdout.strip():
                has_connected = True
    except Exception:
        pass

    return powered, has_connected

def main():
    powered, has_connected = get_bluetooth_info()
    
    classes = ["bluetooth-module"]
    if not powered:
        icon = "󰂲"
        classes.append("disabled")
    elif has_connected:
        icon = "󰂱"
        classes.append("connected")
    else:
        icon = "󰂯"
        classes.append("on")

    print(json.dumps({
        "text": icon,
        "alt": "bluetooth",
        "tooltip": False,
        "class": classes
    }))

if __name__ == "__main__":
    main()
