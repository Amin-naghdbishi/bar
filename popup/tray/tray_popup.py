#!/usr/bin/env python3
"""
System Tray Overflow Popup for Niri
Features:
- Displays background running applications (Telegram, Discord, Hiddify, Delta Chat, Anki, Steam, etc.)
- Attached visually right above the tray button
- Fast launch/focus on click
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
    {"name": "Telegram", "process": "telegram-desktop", "glyph": "", "desc": "Messaging"},
    {"name": "Discord", "process": "discord", "glyph": "", "desc": "Voice & Chat"},
    {"name": "Hiddify", "process": "hiddify", "glyph": "󰒄", "desc": "VPN / Proxy Client"},
    {"name": "Delta Chat", "process": "deltachat", "glyph": "󰭹", "desc": "Decentralized Chat"},
    {"name": "Anki", "process": "anki", "glyph": "󰠮", "desc": "Flashcard Study"},
    {"name": "Spotify", "process": "spotify", "glyph": "", "desc": "Music Streaming"},
    {"name": "Steam", "process": "steam", "glyph": "󰓓", "desc": "Gaming Platform"},
    {"name": "Bitwarden", "process": "bitwarden", "glyph": "󰞀", "desc": "Password Vault"},
    {"name": "Nextcloud", "process": "nextcloud", "glyph": "󰒋", "desc": "Cloud Sync"}
]

def check_process_running(proc_name):
    try:
        p = subprocess.run(["pgrep", "-f", proc_name], capture_output=True, timeout=1)
        return p.returncode == 0
    except Exception:
        return False

class TrayPopup(BasePopupWindow):
    def __init__(self):
        super().__init__(title="System Tray", width=320, anchor="right", name="tray")
        if not HAS_GI:
            return

        self._build_ui()

    def _build_ui(self):
        # 1. Header
        header = self.create_header("System Tray", "Background Apps", "󰅃")
        self.root_box.pack_start(header, False, False, 0)

        # 2. Tray Apps Card
        card = self.create_card()

        # Check running background apps
        running_tray_apps = []
        for app in TRAY_APPS_DATABASE:
            if check_process_running(app["process"]):
                running_tray_apps.append(app)

        if not running_tray_apps:
            # If none detected running, show common quick access
            running_tray_apps = TRAY_APPS_DATABASE[:4]

        # Render in a clean grid / list
        for app in running_tray_apps:
            btn = Gtk.Button()
            btn.get_style_context().add_class("action-btn")

            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            lbl_icon = Gtk.Label()
            lbl_icon.set_markup(f"<span font='14' color='#38bdf8'>{app['glyph']}</span>")
            row.pack_start(lbl_icon, False, False, 0)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            lbl_name = Gtk.Label()
            lbl_name.set_markup(f"<b>{app['name']}</b>")
            lbl_name.set_xalign(0)
            vbox.pack_start(lbl_name, False, False, 0)

            lbl_desc = Gtk.Label(label=app["desc"])
            lbl_desc.set_xalign(0)
            lbl_desc.get_style_context().add_class("popup-subtitle")
            vbox.pack_start(lbl_desc, False, False, 0)

            row.pack_start(vbox, True, True, 0)

            lbl_status = Gtk.Label(label="Running")
            lbl_status.get_style_context().add_class("popup-subtitle")
            row.pack_end(lbl_status, False, False, 0)

            btn.add(row)
            btn.connect("clicked", lambda b, pr=app["process"]: self._on_app_click(pr))

            card.pack_start(btn, False, False, 2)

        self.root_box.pack_start(card, False, False, 0)

    def _on_app_click(self, process_name):
        self.close()
        subprocess.Popen(process_name, shell=True)

if __name__ == "__main__":
    app = TrayPopup()
    app.run()
