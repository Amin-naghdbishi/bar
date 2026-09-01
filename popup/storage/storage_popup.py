#!/usr/bin/env python3
"""
Interactive Storage Center Popup for Niri
Features:
- Root (/) and Home (~/) partition usage bars and statistics
- Category breakdown (Downloads, Videos, Pictures, Documents, Music)
- Sorted largest categories first
- Quick open buttons to launch File Manager
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from popup.common.base import BasePopupWindow, HAS_GI
from popup.storage.backend import StorageBackend

if HAS_GI:
    from gi.repository import Gtk, GLib

class StoragePopup(BasePopupWindow):
    def __init__(self):
        super().__init__(title="Storage Center", width=360, anchor="right", name="storage")
        if not HAS_GI:
            return

        self._build_ui()

    def _build_ui(self):
        # Header
        header = self.create_header("Storage Center", "Disks & Partitions", "󰋊")
        self.root_box.pack_start(header, False, False, 0)

        # Scroller
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_propagate_natural_height(True)
        scroller.set_max_content_height(500)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroller.add(content_box)
        self.root_box.pack_start(scroller, True, True, 0)

        # 1. Main Drives / Partitions Overview
        content_box.pack_start(self.create_section_title("Partitions"), False, False, 0)
        part_card = self.create_card()

        # Root Partition
        root_data = StorageBackend.get_mount_usage("/")
        self._add_partition_row(part_card, "Root (/)", root_data)

        # Home Partition
        home_path = str(Path.home())
        home_data = StorageBackend.get_mount_usage(home_path)
        self._add_partition_row(part_card, "Home (~)", home_data)

        content_box.pack_start(part_card, False, False, 0)

        # 2. Categories Breakdown (Sorted Largest First)
        content_box.pack_start(self.create_section_title("Category Breakdown"), False, False, 0)
        cat_card = self.create_card()

        categories = StorageBackend.get_category_breakdown()
        for cat in categories:
            row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            
            top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            
            lbl_name = Gtk.Label()
            lbl_name.set_markup(f"<b>{cat['icon']} {cat['name']}</b>")
            lbl_name.set_xalign(0)
            top_box.pack_start(lbl_name, True, True, 0)

            lbl_sz = Gtk.Label(label=f"{cat['size_gb']:.2f} GB")
            lbl_sz.get_style_context().add_class("popup-subtitle")
            top_box.pack_start(lbl_sz, False, False, 0)

            btn_open = Gtk.Button(label="Open")
            btn_open.get_style_context().add_class("action-btn")
            btn_open.connect("clicked", lambda b, p=cat["path"]: (self.close(), StorageBackend.open_folder(p)))
            top_box.pack_end(btn_open, False, False, 0)

            row.pack_start(top_box, False, False, 0)

            pbar = Gtk.ProgressBar()
            pbar.set_fraction(max(0.02, cat["fraction"]))
            row.pack_start(pbar, False, False, 0)

            cat_card.pack_start(row, False, False, 3)

        content_box.pack_start(cat_card, False, False, 0)

    def _add_partition_row(self, card_box, label_name, data):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl_title = Gtk.Label()
        lbl_title.set_markup(f"<b>{label_name}</b>")
        lbl_title.set_xalign(0)
        top.pack_start(lbl_title, True, True, 0)

        lbl_stats = Gtk.Label(label=f"{data['used_gb']:.1f} / {data['total_gb']:.1f} GB ({int(data['percentage']*100)}%)")
        lbl_stats.get_style_context().add_class("popup-subtitle")
        top.pack_end(lbl_stats, False, False, 0)

        box.pack_start(top, False, False, 0)

        pbar = Gtk.ProgressBar()
        pbar.set_fraction(data['percentage'])
        if data['percentage'] > 0.9:
            pbar.get_style_context().add_class("danger")
        elif data['percentage'] > 0.8:
            pbar.get_style_context().add_class("warning")
        box.pack_start(pbar, False, False, 0)

        card_box.pack_start(box, False, False, 3)

if __name__ == "__main__":
    app = StoragePopup()
    app.run()
