#!/usr/bin/env python3
"""
Application Right-Click Context Menu Popup for Niri
Features:
- Open new window
- Close active window
- Pin / Unpin from taskbar
- Toggle Launch at startup (autostart)
- Quit application
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from popup.common.base import BasePopupWindow, HAS_GI

if HAS_GI:
    from gi.repository import Gtk, GLib

def is_autostart_enabled(app_id):
    autostart_dir = Path.home() / ".config" / "autostart"
    desktop_file = autostart_dir / f"{app_id}.desktop"
    return desktop_file.exists()

def toggle_autostart(app_id, name, exec_cmd):
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    desktop_file = autostart_dir / f"{app_id}.desktop"

    if desktop_file.exists():
        desktop_file.unlink()
        return False
    else:
        content = f"""[Desktop Entry]
Type=Application
Name={name}
Exec={exec_cmd}
Icon={app_id}
X-GNOME-Autostart-enabled=true
"""
        desktop_file.write_text(content)
        return True

class ContextMenuPopup(BasePopupWindow):
    def __init__(self, app_id, name, exec_cmd, is_pinned=False, is_running=False):
        super().__init__(title=f"{name} Menu", width=260, anchor="center", name="context_menu")
        if not HAS_GI:
            return
        self.app_id = app_id
        self.name = name or app_id.capitalize()
        self.exec_cmd = exec_cmd or app_id
        self.is_pinned = is_pinned
        self.is_running = is_running
        self._build_ui()

    def _build_ui(self):
        header = self.create_header(self.name, "Application Options", "󰣆")
        self.root_box.pack_start(header, False, False, 0)

        card = self.create_card()

        # 1. Open New Window
        self._add_action_row(card, "󰖲  Open New Window", self._on_open_new)

        # 2. Close Window (if running)
        if self.is_running:
            self._add_action_row(card, "󰅖  Close Window", self._on_close_window)

        # 3. Pin / Unpin Toggle
        pin_label = "󰤱  Unpin from Taskbar" if self.is_pinned else "󰤰  Pin to Taskbar"
        self._add_action_row(card, pin_label, self._on_toggle_pin)

        # 4. Launch at Startup Toggle
        autostart_active = is_autostart_enabled(self.app_id)
        auto_label = "󰓛  Disable Startup Launch" if autostart_active else "󰓚  Launch at Startup"
        self._add_action_row(card, auto_label, self._on_toggle_autostart)

        # 5. Quit Application (if running)
        if self.is_running:
            self._add_action_row(card, "󰐥  Quit Application", self._on_quit_app, is_danger=True)

        self.root_box.pack_start(card, False, False, 0)

    def _add_action_row(self, card_box, label_text, callback, is_danger=False):
        btn = Gtk.Button(label=label_text)
        btn.get_style_context().add_class("action-btn")
        if is_danger:
            btn.get_style_context().add_class("danger")
        btn.set_xalign(0)
        btn.connect("clicked", lambda b: callback())
        card_box.pack_start(btn, False, False, 2)

    def _on_open_new(self):
        self.close()
        subprocess.Popen(self.exec_cmd, shell=True)

    def _on_close_window(self):
        self.close()
        # Find window id for this app and close it
        try:
            p = subprocess.run(["niri", "msg", "-j", "windows"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0:
                import json
                for w in json.loads(p.stdout):
                    w_app = (w.get("app_id") or "").lower()
                    if self.app_id.lower() in w_app:
                        subprocess.run(["niri", "msg", "action", "close-window", "--id", str(w["id"])])
                        break
        except Exception:
            pass

    def _on_toggle_pin(self):
        self.close()
        script_path = Path(__file__).resolve().parent.parent.parent / "scripts" / "taskbar.py"
        subprocess.run([sys.executable, str(script_path), "--pin-toggle", self.app_id, self.name, self.exec_cmd])

    def _on_toggle_autostart(self):
        self.close()
        toggle_autostart(self.app_id, self.name, self.exec_cmd)

    def _on_quit_app(self):
        self.close()
        subprocess.run(["killall", "-9", self.app_id])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default="firefox")
    parser.add_argument("--name", default="Firefox")
    parser.add_argument("--exec", default="firefox")
    parser.add_argument("--pinned", default="0")
    parser.add_argument("--running", default="0")
    args = parser.parse_args()

    app = ContextMenuPopup(
        app_id=args.app,
        name=args.name,
        exec_cmd=getattr(args, "exec"),
        is_pinned=(args.pinned == "1"),
        is_running=(args.running == "1")
    )
    app.run()
