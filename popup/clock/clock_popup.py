#!/usr/bin/env python3
"""
Interactive Modern Clock & Calendar Popup for Niri
Features:
- Large digital clock with seconds
- Full formatted date
- Interactive GTK Calendar widget with week numbers
- System time details (Timezone, UTC, Day of year, System Uptime)
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from popup.common.base import BasePopupWindow, HAS_GI

if HAS_GI:
    from gi.repository import Gtk, GLib

def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            if hours > 24:
                days = hours // 24
                rem_hours = hours % 24
                return f"{days}d {rem_hours}h {minutes}m"
            return f"{hours}h {minutes}m"
    except Exception:
        return "Unknown"

class ClockPopup(BasePopupWindow):
    def __init__(self):
        super().__init__(title="Calendar & Time", width=340, anchor="right", name="clock")
        if not HAS_GI:
            return

        self._build_ui()
        # Update clock every second
        GLib.timeout_add(1000, self._update_time)

    def _build_ui(self):
        # 1. Header
        header = self.create_header("Date & Time", "System Calendar", "󰥔")
        self.root_box.pack_start(header, False, False, 0)

        # 2. Large Digital Clock Card
        clock_card = self.create_card()
        
        self.lbl_clock = Gtk.Label()
        self.lbl_clock.set_markup(f"<span font='28' weight='bold' color='#f8fafc'>{datetime.now().strftime('%H:%M:%S')}</span>")
        self.lbl_clock.set_xalign(0.5)
        clock_card.pack_start(self.lbl_clock, False, False, 2)

        self.lbl_date = Gtk.Label()
        self.lbl_date.set_markup(f"<span size='medium' color='#38bdf8' weight='semibold'>{datetime.now().strftime('%A, %B %d, %Y')}</span>")
        self.lbl_date.set_xalign(0.5)
        clock_card.pack_start(self.lbl_date, False, False, 2)

        self.root_box.pack_start(clock_card, False, False, 0)

        # 3. Interactive GTK Calendar
        self.calendar = Gtk.Calendar()
        self.calendar.set_display_options(
            Gtk.CalendarDisplayOptions.SHOW_HEADING |
            Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES |
            Gtk.CalendarDisplayOptions.SHOW_WEEK_NUMBERS
        )
        self.root_box.pack_start(self.calendar, False, False, 0)

        # 4. Time Information Card
        info_card = self.create_card()
        
        now = datetime.now()
        tz_name = time.tzname[0] if time.tzname else "Local"
        utc_offset = now.strftime("%z")
        if utc_offset:
            utc_offset = f"UTC{utc_offset[:3]}:{utc_offset[3:]}"
        else:
            utc_offset = "UTC"

        day_of_year = now.strftime("%j")
        week_num = now.strftime("%V")
        uptime_str = get_uptime()

        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_row_spacing(6)

        def add_info_row(row, label_text, value_text):
            lbl_k = Gtk.Label(label=label_text)
            lbl_k.set_xalign(0)
            lbl_k.get_style_context().add_class("popup-subtitle")
            
            lbl_v = Gtk.Label()
            lbl_v.set_markup(f"<b>{value_text}</b>")
            lbl_v.set_xalign(1)
            
            grid.attach(lbl_k, 0, row, 1, 1)
            grid.attach(lbl_v, 1, row, 1, 1)

        add_info_row(0, "Timezone", f"{tz_name} ({utc_offset})")
        add_info_row(1, "Week of Year", f"Week {week_num}")
        add_info_row(2, "Day of Year", f"Day {day_of_year} / 365")
        add_info_row(3, "System Uptime", uptime_str)

        info_card.pack_start(grid, True, True, 0)
        self.root_box.pack_start(info_card, False, False, 0)

    def _update_time(self):
        now = datetime.now()
        self.lbl_clock.set_markup(f"<span font='28' weight='bold' color='#f8fafc'>{now.strftime('%H:%M:%S')}</span>")
        self.lbl_date.set_markup(f"<span size='medium' color='#38bdf8' weight='semibold'>{now.strftime('%A, %B %d, %Y')}</span>")
        return True

if __name__ == "__main__":
    app = ClockPopup()
    app.run()
