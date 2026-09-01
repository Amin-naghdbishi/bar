#!/usr/bin/env python3
"""
Interactive Keyboard Layout Selector Popup for Niri
Features:
- Lists all active keyboard layouts (English, Persian, etc.)
- Highlights current active layout
- Instant layout switching on click
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from popup.common.base import BasePopupWindow, HAS_GI
from popup.keyboard.backend import KeyboardBackend

if HAS_GI:
    from gi.repository import Gtk, GLib

class KeyboardPopup(BasePopupWindow):
    def __init__(self):
        super().__init__(title="Keyboard Layouts", width=340, anchor="right", name="keyboard")
        if not HAS_GI:
            return

        self._build_ui()

    def _build_ui(self):
        # 1. Header
        header = self.create_header("Keyboard", "Input Layouts", "󰌌")
        self.root_box.pack_start(header, False, False, 0)

        layouts, cur_idx = KeyboardBackend.get_layouts()

        # 2. Layouts list card
        self.root_box.pack_start(self.create_section_title("Available Layouts"), False, False, 0)
        card = self.create_card()

        for lay in layouts:
            row_btn = Gtk.Button()
            row_btn.get_style_context().add_class("action-btn")
            if lay["is_active"]:
                row_btn.get_style_context().add_class("active")

            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            lbl_code = Gtk.Label()
            lbl_code.set_markup(f"<span font='14' weight='bold' color='#38bdf8'>{lay['code']}</span>")
            box.pack_start(lbl_code, False, False, 0)

            lbl_name = Gtk.Label()
            active_mark = " ✓ (Active)" if lay["is_active"] else ""
            lbl_name.set_markup(f"<b>{lay['name']}</b>{active_mark}")
            lbl_name.set_xalign(0)
            box.pack_start(lbl_name, True, True, 0)

            row_btn.add(box)
            row_btn.connect("clicked", lambda b, idx=lay["idx"]: (KeyboardBackend.switch_to_layout(idx), self.close()))

            card.pack_start(row_btn, False, False, 2)

        self.root_box.pack_start(card, False, False, 0)

        # 3. Tip card
        tip_card = self.create_card()
        lbl_tip = Gtk.Label()
        lbl_tip.set_markup("<span size='small' color='#94a3b8'>Tip: Press <b>Mod+Space</b> in Niri to switch layouts quickly.</span>")
        lbl_tip.set_xalign(0)
        lbl_tip.set_line_wrap(True)
        tip_card.pack_start(lbl_tip, False, False, 0)
        self.root_box.pack_start(tip_card, False, False, 0)

if __name__ == "__main__":
    app = KeyboardPopup()
    app.run()
