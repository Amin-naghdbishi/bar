#!/usr/bin/env python3
"""
Clean Storage Status for Waybar
Requirements:
- Disk icon ONLY (no percentage text in main bar)
- Tooltip with root and /home usage overview
"""

import json
import shutil
import sys
from pathlib import Path

def get_disk_usage(path_str):
    try:
        usage = shutil.disk_usage(path_str)
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        pct = int((usage.used / usage.total) * 100)
        return total_gb, used_gb, free_gb, pct
    except Exception:
        return 0, 0, 0, 0

def main():
    root_tot, root_used, root_free, root_pct = get_disk_usage("/")
    home_path = str(Path.home())
    home_tot, home_used, home_free, home_pct = get_disk_usage(home_path)

    classes = ["storage-module"]
    if root_pct > 90 or home_pct > 90:
        classes.append("critical")
    elif root_pct > 80 or home_pct > 80:
        classes.append("warning")

    tooltip = (
        f"<b>Storage Overview</b>\n"
        f"• Root (/): {root_pct}% used ({root_used:.1f} / {root_tot:.1f} GB)\n"
        f"• Home (~): {home_pct}% used ({home_used:.1f} / {home_tot:.1f} GB)\n\n"
        f"<i>Click to open Storage Center</i>"
    )

    print(json.dumps({
        "text": "󰋊",
        "alt": "storage",
        "tooltip": tooltip,
        "class": classes,
        "percentage": max(root_pct, home_pct)
    }))

if __name__ == "__main__":
    main()
