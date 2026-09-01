#!/usr/bin/env python3
"""
Clean Audio Status for Waybar
- Speaker icon ONLY
- Dynamic icon based on volume level and mute state
- No tooltips (clicking opens the real Audio Center popup window)
"""

import json
import re
import subprocess
import sys

def get_audio_info():
    vol = 70
    is_muted = False

    try:
        proc = subprocess.run(
            ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if proc.returncode == 0:
            out = proc.stdout.strip()
            m = re.search(r"Volume:\s*([\d\.]+)", out)
            if m:
                vol = int(float(m.group(1)) * 100)
            if "[MUTED]" in out:
                is_muted = True
    except Exception:
        try:
            proc = subprocess.run(
                ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if proc.returncode == 0:
                m = re.search(r"(\d+)%", proc.stdout)
                if m:
                    vol = int(m.group(1))
            proc_mute = subprocess.run(
                ["pactl", "get-sink-mute", "@DEFAULT_SINK@"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if "yes" in proc_mute.stdout.lower():
                is_muted = True
        except Exception:
            pass

    return vol, is_muted

def main():
    vol, is_muted = get_audio_info()
    
    classes = ["audio-module"]
    if is_muted or vol <= 0:
        icon = "󰝟"
        classes.append("muted")
    elif vol < 33:
        icon = "󰕿"
    elif vol < 66:
        icon = "󰖀"
    else:
        icon = "󰕾"

    print(json.dumps({
        "text": icon,
        "alt": f"audio-{vol}",
        "tooltip": False,
        "class": classes,
        "percentage": vol
    }))

if __name__ == "__main__":
    main()
