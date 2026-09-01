#!/usr/bin/env python3
"""
Clean Audio Status for Waybar
Requirements:
- Single speaker icon ONLY (no separate mic icon on the bar)
- No volume percentage text in the main bar
- Dynamic speaker icon based on volume level and mute state
- Rich tooltip with sink, volume %, and microphone status
"""

import json
import os
import re
import subprocess
import sys

def get_audio_info():
    vol = 70
    is_muted = False
    sink_name = "Default Output"
    mic_muted = False

    # Try wpctl (WirePlumber / PipeWire)
    try:
        proc = subprocess.run(
            ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if proc.returncode == 0:
            out = proc.stdout.strip()
            # Format: "Volume: 0.70 [MUTED]"
            m = re.search(r"Volume:\s*([\d\.]+)", out)
            if m:
                vol = int(float(m.group(1)) * 100)
            if "[MUTED]" in out:
                is_muted = True
    except Exception:
        # Fallback to pactl
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

    # Check mic mute state
    try:
        proc = subprocess.run(
            ["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if "[MUTED]" in proc.stdout:
            mic_muted = True
    except Exception:
        pass

    return vol, is_muted, sink_name, mic_muted

def main():
    vol, is_muted, sink_name, mic_muted = get_audio_info()
    
    classes = ["audio-module"]
    if is_muted:
        icon = "󰝟"
        classes.append("muted")
    elif vol <= 0:
        icon = "󰝟"
        classes.append("muted")
    elif vol < 33:
        icon = "󰕿"
    elif vol < 66:
        icon = "󰖀"
    else:
        icon = "󰕾"

    mic_status_str = "Muted" if mic_muted else "Active"
    vol_status_str = f"{vol}%" if not is_muted else "Muted"
    
    tooltip = (
        f"<b>Audio Center</b>\n"
        f"• Output Volume: {vol_status_str}\n"
        f"• Microphone: {mic_status_str}\n\n"
        f"<i>Left-click to open Audio Center\n"
        f"Right-click to toggle mute\n"
        f"Scroll to adjust volume</i>"
    )

    print(json.dumps({
        "text": icon,
        "alt": f"audio-{vol}",
        "tooltip": tooltip,
        "class": classes,
        "percentage": vol
    }))

if __name__ == "__main__":
    main()
