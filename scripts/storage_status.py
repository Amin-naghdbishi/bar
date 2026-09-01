#!/usr/bin/env python3
"""
Clean Storage Status for Waybar
- Disk icon ONLY
- No tooltips (clicking opens the real Storage Center popup window)
"""

import json
import shutil
import sys
from pathlib import Path

def get_disk_usage(path_str):
    try:
        usage = shutil.disk_usage(path_str)
        pct = int((usage.used / usage.total) * 100)
        return pct
    except Exception:
        return 0

def main():
    root_pct = get_disk_usage("/")
    home_path = str(Path.home())
    home_pct = get_disk_usage(home_path)
    max_pct = max(root_pct, home_pct)

    classes = ["storage-module"]
    if max_pct > 90:
        classes.append("critical")
    elif max_pct > 80:
        classes.append("warning")

    print(json.dumps({
        "text": "󰋊",
        "alt": "storage",
        "tooltip": False,
        "class": classes,
        "percentage": max_pct
    }))

if __name__ == "__main__":
    main()
