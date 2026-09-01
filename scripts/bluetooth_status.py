#!/usr/bin/env python3
"""
Clean Bluetooth Status for Waybar
Requirements:
- Bluetooth icon ONLY (no text in main bar)
- State indication: connected, powered on, powered off
- Tooltip with connected device names
"""

import json
import subprocess
import sys

def get_bluetooth_info():
    powered = False
    connected_devices = []

    try:
        proc = subprocess.run(
            ["bluetoothctl", "show"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if proc.returncode == 0:
            if "Powered: yes" in proc.stdout:
                powered = True

        if powered:
            proc_dev = subprocess.run(
                ["bluetoothctl", "devices", "Connected"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if proc_dev.returncode == 0:
                for line in proc_dev.stdout.splitlines():
                    parts = line.strip().split(" ", 2)
                    if len(parts) >= 3:
                        connected_devices.append(parts[2])
    except Exception:
        pass

    return powered, connected_devices

def main():
    powered, connected_devices = get_bluetooth_info()
    
    classes = ["bluetooth-module"]
    if not powered:
        icon = "󰂲"
        classes.append("disabled")
        tooltip = "<b>Bluetooth Center</b>\n• Status: Powered Off\n\n<i>Click to open Bluetooth Center</i>"
    elif connected_devices:
        icon = "󰂱"
        classes.append("connected")
        dev_list = "\n".join([f"  • {d}" for d in connected_devices])
        tooltip = f"<b>Bluetooth Center</b>\n• Status: Connected\n<b>Connected Devices:</b>\n{dev_list}\n\n<i>Click to open Bluetooth Center</i>"
    else:
        icon = "󰂯"
        classes.append("on")
        tooltip = "<b>Bluetooth Center</b>\n• Status: On (No devices connected)\n\n<i>Click to open Bluetooth Center</i>"

    print(json.dumps({
        "text": icon,
        "alt": "bluetooth",
        "tooltip": tooltip,
        "class": classes
    }))

if __name__ == "__main__":
    main()
