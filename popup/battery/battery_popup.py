#!/usr/bin/env python3
"""
Interactive Battery and Power Center Popup for Niri
Features:
- Battery status, remaining time estimate, and AC power status
- Power profile selector (Performance, Balanced, Power Saver)
- Brightness slider
- Night Light (Blue Light Filter) toggle
- 80% Battery Protection toggle
- System power actions (Lock, Suspend, Reboot, Shutdown)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from popup.common.base import BasePopupWindow, HAS_GI
from popup.battery.backend import BatteryBackend

if HAS_GI:
    from gi.repository import Gtk, GLib

class BatteryPopup(BasePopupWindow):
    def __init__(self):
        super().__init__(title="Battery & Power", width=380, anchor="right", name="battery")
        if not HAS_GI:
            return

        self._build_ui()

    def _build_ui(self):
        # 1. Header
        header = self.create_header("Battery & Power", "System Power Management", "󰂄")
        self.root_box.pack_start(header, False, False, 0)

        # Scroller
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_propagate_natural_height(True)
        scroller.set_max_content_height(500)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scroller.add(content_box)
        self.root_box.pack_start(scroller, True, True, 0)

        info = BatteryBackend.get_power_info()

        # 2. Battery & Power Status Card
        status_card = self.create_card()
        
        stat_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Big percentage badge
        lbl_pct = Gtk.Label()
        lbl_pct.set_markup(f"<span font='26' weight='bold' color='#38bdf8'>{info['capacity']}%</span>")
        stat_top.pack_start(lbl_pct, False, False, 0)

        # Status text
        stat_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl_stat = Gtk.Label()
        ac_str = "Using Charger" if info["is_ac"] or "charg" in info["status"].lower() else "Using Battery"
        lbl_stat.set_markup(f"<b>{ac_str}</b> ({info['status']})")
        lbl_stat.set_xalign(0)
        stat_vbox.pack_start(lbl_stat, False, False, 0)

        if info["time_remaining"]:
            lbl_rem = Gtk.Label(label=info["time_remaining"])
            lbl_rem.set_xalign(0)
            lbl_rem.get_style_context().add_class("popup-subtitle")
            stat_vbox.pack_start(lbl_rem, False, False, 0)

        stat_top.pack_start(stat_vbox, True, True, 0)
        status_card.pack_start(stat_top, False, False, 0)

        # Progress bar
        pbar = Gtk.ProgressBar()
        pbar.set_fraction(info["capacity"] / 100.0)
        if info["capacity"] <= 15:
            pbar.get_style_context().add_class("danger")
        elif info["capacity"] <= 30:
            pbar.get_style_context().add_class("warning")
        status_card.pack_start(pbar, False, False, 2)

        content_box.pack_start(status_card, False, False, 0)

        # 3. Power Modes (Performance / Balanced / Power Saver)
        content_box.pack_start(self.create_section_title("Power Mode"), False, False, 0)
        modes_card = self.create_card()
        modes_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        current_profile = BatteryBackend.get_power_profile().lower()

        self.btn_power_saver = Gtk.Button(label="󰌪 Saver")
        self.btn_power_saver.get_style_context().add_class("action-btn")
        if "saver" in current_profile:
            self.btn_power_saver.get_style_context().add_class("active")
        self.btn_power_saver.connect("clicked", lambda b: self._on_set_profile("power-saver"))
        modes_box.pack_start(self.btn_power_saver, True, True, 0)

        self.btn_balanced = Gtk.Button(label="󰾅 Balanced")
        self.btn_balanced.get_style_context().add_class("action-btn")
        if "balanced" in current_profile:
            self.btn_balanced.get_style_context().add_class("active")
        self.btn_balanced.connect("clicked", lambda b: self._on_set_profile("balanced"))
        modes_box.pack_start(self.btn_balanced, True, True, 0)

        self.btn_perf = Gtk.Button(label="󰓅 Perf")
        self.btn_perf.get_style_context().add_class("action-btn")
        if "performance" in current_profile:
            self.btn_perf.get_style_context().add_class("active")
        self.btn_perf.connect("clicked", lambda b: self._on_set_profile("performance"))
        modes_box.pack_start(self.btn_perf, True, True, 0)

        modes_card.pack_start(modes_box, False, False, 0)
        content_box.pack_start(modes_card, False, False, 0)

        # 4. Display Brightness Slider
        content_box.pack_start(self.create_section_title("Display Brightness"), False, False, 0)
        bright_card = self.create_card()
        bright_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        lbl_b_icon = Gtk.Label(label="󰃠")
        lbl_b_icon.get_style_context().add_class("popup-subtitle")
        bright_box.pack_start(lbl_b_icon, False, False, 0)

        cur_bright = BatteryBackend.get_brightness()
        self.scale_bright = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 5, 100, 1)
        self.scale_bright.set_value(cur_bright)
        self.scale_bright.set_hexpand(True)
        self.scale_bright.connect("value-changed", self._on_bright_changed)
        bright_box.pack_start(self.scale_bright, True, True, 0)

        self.lbl_bright_pct = Gtk.Label(label=f"{cur_bright}%")
        self.lbl_bright_pct.set_width_chars(4)
        bright_box.pack_start(self.lbl_bright_pct, False, False, 0)

        bright_card.pack_start(bright_box, False, False, 0)
        content_box.pack_start(bright_card, False, False, 0)

        # 5. Night Light & Battery Protection Toggles
        content_box.pack_start(self.create_section_title("Features & Protection"), False, False, 0)
        feats_card = self.create_card()

        # Night Light
        nl_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl_nl = Gtk.Label(label="󰖔 Night Light (Blue Light Filter)")
        lbl_nl.set_xalign(0)
        nl_row.pack_start(lbl_nl, True, True, 0)

        sw_nl = Gtk.Switch()
        sw_nl.set_active(BatteryBackend.is_night_light_active())
        sw_nl.connect("notify::active", lambda s, p: BatteryBackend.toggle_night_light())
        nl_row.pack_end(sw_nl, False, False, 0)
        feats_card.pack_start(nl_row, False, False, 2)

        # Battery 80% Protection
        prot_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl_prot = Gtk.Label(label="󰂄 Battery Protection (80% Limit)")
        lbl_prot.set_xalign(0)
        prot_row.pack_start(lbl_prot, True, True, 0)

        sw_prot = Gtk.Switch()
        sw_prot.set_active(BatteryBackend.get_battery_limit_status())
        sw_prot.connect("notify::active", lambda s, p: BatteryBackend.set_battery_limit(s.get_active()))
        prot_row.pack_end(sw_prot, False, False, 0)
        feats_card.pack_start(prot_row, False, False, 2)

        content_box.pack_start(feats_card, False, False, 0)

        # 6. Quick Power Actions
        content_box.pack_start(self.create_section_title("Power Actions"), False, False, 0)
        acts_card = self.create_card()
        acts_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        btn_lock = Gtk.Button(label="󰌾 Lock")
        btn_lock.get_style_context().add_class("action-btn")
        btn_lock.connect("clicked", lambda b: (self.close(), BatteryBackend.execute_power_action("lock")))
        acts_box.pack_start(btn_lock, True, True, 0)

        btn_sleep = Gtk.Button(label="󰒲 Sleep")
        btn_sleep.get_style_context().add_class("action-btn")
        btn_sleep.connect("clicked", lambda b: (self.close(), BatteryBackend.execute_power_action("suspend")))
        acts_box.pack_start(btn_sleep, True, True, 0)

        btn_reboot = Gtk.Button(label="󰜉 Reboot")
        btn_reboot.get_style_context().add_class("action-btn")
        btn_reboot.connect("clicked", lambda b: (self.close(), BatteryBackend.execute_power_action("reboot")))
        acts_box.pack_start(btn_reboot, True, True, 0)

        btn_off = Gtk.Button(label="󰐥 Off")
        btn_off.get_style_context().add_class("action-btn")
        btn_off.get_style_context().add_class("danger")
        btn_off.connect("clicked", lambda b: (self.close(), BatteryBackend.execute_power_action("poweroff")))
        acts_box.pack_start(btn_off, True, True, 0)

        acts_card.pack_start(acts_box, False, False, 0)
        content_box.pack_start(acts_card, False, False, 0)

    def _on_set_profile(self, profile):
        BatteryBackend.set_power_profile(profile)
        self.btn_power_saver.get_style_context().remove_class("active")
        self.btn_balanced.get_style_context().remove_class("active")
        self.btn_perf.get_style_context().remove_class("active")
        
        if profile == "power-saver":
            self.btn_power_saver.get_style_context().add_class("active")
        elif profile == "balanced":
            self.btn_balanced.get_style_context().add_class("active")
        elif profile == "performance":
            self.btn_perf.get_style_context().add_class("active")

    def _on_bright_changed(self, scale):
        val = int(scale.get_value())
        self.lbl_bright_pct.set_text(f"{val}%")
        BatteryBackend.set_brightness(val)

if __name__ == "__main__":
    app = BatteryPopup()
    app.run()
