#!/usr/bin/env python3
"""
Interactive Bluetooth Center Popup for Niri
Features:
- Master Bluetooth Toggle (ON / OFF)
- Scan for nearby devices
- Connected devices list (with Disconnect & Battery %)
- Paired & Available devices list (with Connect, Pair)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from popup.common.base import BasePopupWindow, HAS_GI
from popup.bluetooth.backend import BluetoothBackend

if HAS_GI:
    from gi.repository import Gtk, GLib

class BluetoothPopup(BasePopupWindow):
    def __init__(self):
        super().__init__(title="Bluetooth Center", width=380, anchor="right", name="bluetooth")
        if not HAS_GI:
            return

        self._build_ui()

    def _build_ui(self):
        # 1. Header
        header = self.create_header("Bluetooth", "Wireless Devices", "󰂯")
        self.root_box.pack_start(header, False, False, 0)

        # Scroller
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_propagate_natural_height(True)
        scroller.set_max_content_height(480)

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scroller.add(self.content_box)
        self.root_box.pack_start(scroller, True, True, 0)

        # 2. Master Toggle & Scan Card
        top_card = self.create_card()
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        lbl_pwr = Gtk.Label(label="Bluetooth Master")
        lbl_pwr.set_xalign(0)
        top_row.pack_start(lbl_pwr, True, True, 0)

        self.sw_power = Gtk.Switch()
        is_pwr = BluetoothBackend.is_powered()
        self.sw_power.set_active(is_pwr)
        self.sw_power.connect("notify::active", self._on_power_toggle)
        top_row.pack_start(self.sw_power, False, False, 0)

        self.btn_scan = Gtk.Button(label="󰂰 Scan")
        self.btn_scan.get_style_context().add_class("action-btn")
        self.btn_scan.connect("clicked", self._on_scan_clicked)
        top_row.pack_end(self.btn_scan, False, False, 0)

        top_card.pack_start(top_row, False, False, 0)
        self.content_box.pack_start(top_card, False, False, 0)

        # 3. Connected Devices Section
        self.content_box.pack_start(self.create_section_title("Connected Devices"), False, False, 0)
        self.conn_card = self.create_card()
        self._populate_connected_devices()
        self.content_box.pack_start(self.conn_card, False, False, 0)

        # 4. Paired & Available Devices Section
        self.content_box.pack_start(self.create_section_title("Paired & Available Devices"), False, False, 0)
        self.avail_card = self.create_card()
        self._populate_available_devices()
        self.content_box.pack_start(self.avail_card, False, False, 0)

    def _populate_connected_devices(self):
        # Clear existing
        for c in self.conn_card.get_children():
            self.conn_card.remove(c)

        connected = BluetoothBackend.get_connected_devices()
        if not connected:
            lbl_none = Gtk.Label(label="No devices connected")
            lbl_none.get_style_context().add_class("popup-subtitle")
            self.conn_card.pack_start(lbl_none, False, False, 4)
            return

        for dev in connected:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            lbl_icon = Gtk.Label(label=dev["icon"])
            lbl_icon.get_style_context().add_class("popup-title")
            row.pack_start(lbl_icon, False, False, 0)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            lbl_name = Gtk.Label()
            lbl_name.set_markup(f"<b>{dev['name']}</b>")
            lbl_name.set_xalign(0)
            vbox.pack_start(lbl_name, False, False, 0)

            if dev["battery"]:
                lbl_bat = Gtk.Label(label=f"Battery: {dev['battery']}")
                lbl_bat.set_xalign(0)
                lbl_bat.get_style_context().add_class("popup-subtitle")
                vbox.pack_start(lbl_bat, False, False, 0)
            
            row.pack_start(vbox, True, True, 0)

            btn_dis = Gtk.Button(label="Disconnect")
            btn_dis.get_style_context().add_class("action-btn")
            btn_dis.get_style_context().add_class("danger")
            btn_dis.connect("clicked", lambda b, m=dev["mac"]: self._on_disconnect(m))
            row.pack_end(btn_dis, False, False, 0)

            self.conn_card.pack_start(row, False, False, 2)

    def _populate_available_devices(self):
        for c in self.avail_card.get_children():
            self.avail_card.remove(c)

        paired = BluetoothBackend.get_paired_and_available_devices()
        connected_macs = [d["mac"] for d in BluetoothBackend.get_connected_devices()]
        
        # Filter out already connected
        available = [d for d in paired if d["mac"] not in connected_macs]

        if not available:
            lbl_none = Gtk.Label(label="No other paired devices found")
            lbl_none.get_style_context().add_class("popup-subtitle")
            self.avail_card.pack_start(lbl_none, False, False, 4)
            return

        for dev in available:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            lbl_icon = Gtk.Label(label=dev["icon"])
            lbl_icon.get_style_context().add_class("popup-title")
            row.pack_start(lbl_icon, False, False, 0)

            lbl_name = Gtk.Label(label=dev["name"])
            lbl_name.set_xalign(0)
            row.pack_start(lbl_name, True, True, 0)

            btn_conn = Gtk.Button(label="Connect")
            btn_conn.get_style_context().add_class("action-btn")
            btn_conn.connect("clicked", lambda b, m=dev["mac"]: self._on_connect(m))
            row.pack_end(btn_conn, False, False, 0)

            self.avail_card.pack_start(row, False, False, 2)

    def _on_power_toggle(self, switch, gparam):
        pwr = switch.get_active()
        BluetoothBackend.set_power(pwr)
        GLib.timeout_add(800, self._refresh_lists)

    def _on_scan_clicked(self, btn):
        BluetoothBackend.start_scan()
        btn.set_label("󰂰 Scanning...")
        GLib.timeout_add(3000, lambda: btn.set_label("󰂰 Scan") or self._refresh_lists() or False)

    def _on_connect(self, mac):
        BluetoothBackend.connect_device(mac)
        GLib.timeout_add(1500, self._refresh_lists)

    def _on_disconnect(self, mac):
        BluetoothBackend.disconnect_device(mac)
        GLib.timeout_add(800, self._refresh_lists)

    def _refresh_lists(self):
        self._populate_connected_devices()
        self._populate_available_devices()
        self.conn_card.show_all()
        self.avail_card.show_all()
        return False

if __name__ == "__main__":
    app = BluetoothPopup()
    app.run()
