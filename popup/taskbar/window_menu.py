#!/usr/bin/env python3
"""
Window Grouping Selector Popup for Niri
Displays open windows for a given application and focuses the chosen window via Niri IPC.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from popup.common.base import BasePopupWindow, HAS_GI
from scripts.icon_resolver import resolve_app_icon

if HAS_GI:
    from gi.repository import Gtk, GLib

def get_app_windows(app_id):
    windows = []
    try:
        p = subprocess.run(["niri", "msg", "-j", "windows"], capture_output=True, text=True, timeout=1)
        if p.returncode == 0 and p.stdout.strip():
            all_wins = json.loads(p.stdout)
            if isinstance(all_wins, list):
                for w in all_wins:
                    w_app = (w.get("app_id") or w.get("appId") or "").lower()
                    if app_id.lower() in w_app or w_app in app_id.lower():
                        windows.append(w)
    except Exception:
        pass
    return windows

class WindowMenuPopup(BasePopupWindow):
    def __init__(self, app_id):
        super().__init__(title="Window Selector", width=340, anchor="center", name="window_menu")
        if not HAS_GI:
            return
        self.app_id = app_id
        self._build_ui()

    def _build_ui(self):
        windows = get_app_windows(self.app_id)
        app_title = self.app_id.capitalize()
        app_icon = resolve_app_icon(self.app_id)
        header = self.create_header(f"{app_title} Windows", f"{len(windows)} active window(s)", app_icon)
        self.root_box.pack_start(header, False, False, 0)

        card = self.create_card()

        if not windows:
            lbl = Gtk.Label(label="No open windows found for this app.")
            lbl.get_style_context().add_class("popup-subtitle")
            card.pack_start(lbl, False, False, 6)
        else:
            for w in windows:
                w_id = w.get("id")
                w_title = w.get("title") or "Untitled Window"
                is_focused = w.get("is_focused", False)

                row_btn = Gtk.Button()
                row_btn.get_style_context().add_class("action-btn")
                if is_focused:
                    row_btn.get_style_context().add_class("active")

                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                
                # Active dot indicator
                lbl_dot = Gtk.Label()
                lbl_dot.set_markup("<span color='#38bdf8'>•</span>" if is_focused else "<span color='#64748b'>•</span>")
                box.pack_start(lbl_dot, False, False, 0)

                lbl_win = Gtk.Label(label=w_title)
                lbl_win.set_xalign(0)
                lbl_win.set_ellipsize(3) # PANGO_ELLIPSIZE_END
                lbl_win.set_max_width_chars(30)
                box.pack_start(lbl_win, True, True, 0)

                # Close button for this individual window
                btn_close = Gtk.Button(label="✕")
                btn_close.get_style_context().add_class("popup-close-btn")
                btn_close.connect("clicked", lambda b, win_id=w_id: self._close_window(win_id))
                box.pack_end(btn_close, False, False, 0)

                row_btn.add(box)
                row_btn.connect("clicked", lambda b, win_id=w_id: self._focus_window(win_id))

                card.pack_start(row_btn, False, False, 2)

        self.root_box.pack_start(card, False, False, 0)

    def _focus_window(self, win_id):
        self.close()
        if win_id is not None:
            subprocess.run(["niri", "msg", "action", "focus-window", "--id", str(win_id)])

    def _close_window(self, win_id):
        if win_id is not None:
            subprocess.run(["niri", "msg", "action", "close-window", "--id", str(win_id)])
        self.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default="firefox", help="App ID")
    args = parser.parse_args()

    app = WindowMenuPopup(args.app)
    app.run()
