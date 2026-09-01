#!/usr/bin/env python3
"""
System Tray Overflow Popup for Niri
Windows 11-style compact tray attached directly above the taskbar overflow button.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from popup.common.base import BasePopupWindow, HAS_GI

if HAS_GI:
    from gi.repository import Gtk, GLib

TRAY_APPS_DATABASE = [
    {"name": "Telegram", "process": "telegram-desktop", "glyph": ""},
    {"name": "Discord", "process": "discord", "glyph": ""},
    {"name": "Hiddify", "process": "hiddify", "glyph": "󰒄"},
    {"name": "Delta Chat", "process": "deltachat", "glyph": "󰭹"},
    {"name": "Anki", "process": "anki", "glyph": "󰠮"},
    {"name": "Spotify", "process": "spotify", "glyph": ""},
    {"name": "Steam", "process": "steam", "glyph": "󰓓"},
    {"name": "Bitwarden", "process": "bitwarden", "glyph": "󰞀"}
]

def check_process_running(proc_name):
    try:
        p = subprocess.run(["pgrep", "-f", proc_name], capture_output=True, timeout=1)
        return p.returncode == 0
    except Exception:
        return False

class TrayPopup(BasePopupWindow):
    def __init__(self):
        super().__init__(title="Tray Overflow", width=220, anchor="right", name="tray")
        if not HAS_GI:
            return

        self._build_ui()

    def _build_ui(self):
        # Header - Compact
        header = self.create_header("Background Apps", "", "󰅃")
        self.root_box.pack_start(header, False, False, 0)

        # Compact Grid Container
        grid = Gtk.Grid()
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(True)

        running_tray_apps = [a for a in TRAY_APPS_DATABASE if check_process_running(a["process"])]
        if not running_tray_apps:
            running_tray_apps = TRAY_APPS_DATABASE[:6]

        col = 0
        row = 0
        for app in running_tray_apps:
            btn = Gtk.Button()
            btn.get_style_context().add_class("action-btn")
            btn.set_tooltip_text(app["name"])

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            lbl_icon = Gtk.Label()
            lbl_icon.set_markup(f"<span font='16' color='#38bdf8'>{app['glyph']}</span>")
            box.pack_start(lbl_icon, False, False, 2)

            lbl_name = Gtk.Label(label=app["name"])
            lbl_name.get_style_context().add_class("popup-subtitle")
            lbl_name.set_ellipsize(3)
            box.pack_start(lbl_name, False, False, 0)

            btn.add(box)
            btn.connect("clicked", lambda b, pr=app["process"]: self._on_app_click(pr))

            grid.attach(btn, col, row, 1, 1)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        self.root_box.pack_start(grid, True, True, 2)

    def _on_app_click(self, process_name):
        self.close()
        subprocess.Popen(process_name, shell=True)

if __name__ == "__main__":
    app = TrayPopup()
    app.run()
