#!/usr/bin/env python3
"""
Clean Battery Status for Waybar
- Battery icon ONLY
- Dynamic icon based on capacity and charging state
- No tooltips (clicking opens the real Battery & Power Center popup window)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

def get_battery_info():
    capacity = 100
    status = "Discharging"
    is_ac = False
    has_battery = False

    base = Path("/sys/class/power_supply")
    if base.exists():
        for bat in base.glob("BAT*"):
            has_battery = True
            try:
                cap_file = bat / "capacity"
                if cap_file.exists():
                    capacity = int(cap_file.read_text().strip())
                stat_file = bat / "status"
                if stat_file.exists():
                    status = stat_file.read_text().strip()
                break
            except Exception:
                pass
        
        for ac in base.glob("AC*"):
            try:
                online = (ac / "online").read_text().strip()
                if online == "1":
                    is_ac = True
            except Exception:
                pass

    try:
        proc = subprocess.run(["upower", "-e"], capture_output=True, text=True, timeout=1)
        if proc.returncode == 0:
            for line in proc.stdout.splitlines():
                if "battery" in line:
                    has_battery = True
                    info = subprocess.run(["upower", "-i", line.strip()], capture_output=True, text=True, timeout=1)
                    for info_line in info.stdout.splitlines():
                        if "percentage:" in info_line:
                            m = re.search(r"(\d+)%", info_line)
                            if m:
                                capacity = int(m.group(1))
                        elif "state:" in info_line:
                            status = info_line.split(":")[-1].strip().capitalize()
                    break
    except Exception:
        pass

    return capacity, status, is_ac, has_battery

def get_battery_icon(capacity, status, is_ac):
    is_charging = "charg" in status.lower()
    
    if is_charging:
        if capacity >= 95:
            return "󰂅"
        elif capacity >= 80:
            return "󰂋"
        elif capacity >= 60:
            return "󰂉"
        elif capacity >= 40:
            return "󰂈"
        elif capacity >= 20:
            return "󰂇"
        else:
            return "󰢜"
            
    if capacity >= 95:
        return "󰁹"
    elif capacity >= 85:
        return "󰂁"
    elif capacity >= 70:
        return "󰂀"
    elif capacity >= 60:
        return "󰁿"
    elif capacity >= 50:
        return "󰁾"
    elif capacity >= 40:
        return "󰁽"
    elif capacity >= 30:
        return "󰁼"
    elif capacity >= 20:
        return "󰁻"
    elif capacity >= 10:
        return "󰁺"
    else:
        return "󰂃"

def main():
    capacity, status, is_ac, has_battery = get_battery_info()
    
    classes = ["battery-module"]
    if "charg" in status.lower():
        classes.append("charging")
    if is_ac:
        classes.append("plugged")
    if capacity <= 15:
        classes.append("critical")
    elif capacity <= 25:
        classes.append("warning")

    icon = get_battery_icon(capacity, status, is_ac)
    if not has_battery:
        icon = "󰚥"

    print(json.dumps({
        "text": icon,
        "alt": f"battery-{capacity}",
        "tooltip": False,
        "class": classes,
        "percentage": capacity
    }))

if __name__ == "__main__":
    main()
