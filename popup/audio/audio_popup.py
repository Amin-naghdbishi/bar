#!/usr/bin/env python3
"""
Interactive Audio Center Popup for Niri
Features:
- Master Output Volume slider with mute button
- Output device switcher (Speakers, Headphones, HDMI)
- Microphone slider with mute toggle and input device switcher
- Running Application audio streams volume control
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from popup.common.base import BasePopupWindow, HAS_GI
from popup.audio.backend import AudioBackend

if HAS_GI:
    from gi.repository import Gtk, GLib

class AudioPopup(BasePopupWindow):
    def __init__(self):
        super().__init__(title="Audio Center", width=380, anchor="right", name="audio")
        if not HAS_GI:
            return

        self._build_ui()

    def _build_ui(self):
        # 1. Header
        header = self.create_header("Audio Center", "PipeWire / WirePlumber", "󰕾")
        self.root_box.pack_start(header, False, False, 0)

        # Scrolled container for rich controls
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_propagate_natural_height(True)
        scroller.set_max_content_height(480)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scroller.add(content_box)
        self.root_box.pack_start(scroller, True, True, 0)

        # 2. Output Volume Card
        content_box.pack_start(self.create_section_title("Output Volume"), False, False, 0)
        out_card = self.create_card()

        master_vol, is_muted = AudioBackend.get_master_volume()

        out_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.btn_out_mute = Gtk.Button(label="󰝟" if is_muted else "󰕾")
        self.btn_out_mute.get_style_context().add_class("icon-btn")
        self.btn_out_mute.connect("clicked", self._on_out_mute_toggle)
        out_hbox.pack_start(self.btn_out_mute, False, False, 0)

        self.scale_out = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale_out.set_value(master_vol)
        self.scale_out.set_hexpand(True)
        self.scale_out.connect("value-changed", self._on_out_vol_changed)
        out_hbox.pack_start(self.scale_out, True, True, 0)

        self.lbl_out_vol = Gtk.Label(label=f"{master_vol}%")
        self.lbl_out_vol.set_width_chars(4)
        out_hbox.pack_start(self.lbl_out_vol, False, False, 0)

        out_card.pack_start(out_hbox, False, False, 0)

        # Output Devices List
        sinks = AudioBackend.get_sinks()
        if sinks:
            dev_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            for sink in sinks:
                btn_sink = Gtk.Button()
                btn_sink.get_style_context().add_class("action-btn")
                if sink.get("is_default"):
                    btn_sink.get_style_context().add_class("active")
                
                sink_label = f"{'✓ ' if sink.get('is_default') else '  '}{sink['description']}"
                btn_sink.set_label(sink_label)
                btn_sink.connect("clicked", lambda b, s_id=sink["id"]: self._on_sink_select(s_id))
                dev_box.pack_start(btn_sink, False, False, 0)
            out_card.pack_start(dev_box, False, False, 0)

        content_box.pack_start(out_card, False, False, 0)

        # 3. Microphone (Input) Card
        content_box.pack_start(self.create_section_title("Microphone (Input)"), False, False, 0)
        mic_card = self.create_card()

        mic_vol, mic_muted = AudioBackend.get_mic_volume()

        mic_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.btn_mic_mute = Gtk.Button(label="󰍭" if mic_muted else "󰍬")
        self.btn_mic_mute.get_style_context().add_class("icon-btn")
        if mic_muted:
            self.btn_mic_mute.get_style_context().add_class("active")
        self.btn_mic_mute.connect("clicked", self._on_mic_mute_toggle)
        mic_hbox.pack_start(self.btn_mic_mute, False, False, 0)

        self.scale_mic = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale_mic.set_value(mic_vol)
        self.scale_mic.set_hexpand(True)
        self.scale_mic.connect("value-changed", self._on_mic_vol_changed)
        mic_hbox.pack_start(self.scale_mic, True, True, 0)

        self.lbl_mic_vol = Gtk.Label(label=f"{mic_vol}%")
        self.lbl_mic_vol.set_width_chars(4)
        mic_hbox.pack_start(self.lbl_mic_vol, False, False, 0)

        mic_card.pack_start(mic_hbox, False, False, 0)
        content_box.pack_start(mic_card, False, False, 0)

        # 4. Applications Volume Streams
        app_streams = AudioBackend.get_app_streams()
        if app_streams:
            content_box.pack_start(self.create_section_title("Application Streams"), False, False, 0)
            apps_card = self.create_card()
            for st in app_streams:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                
                lbl_app = Gtk.Label(label=st["name"])
                lbl_app.set_xalign(0)
                lbl_app.set_width_chars(12)
                row.pack_start(lbl_app, False, False, 0)

                scale_st = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
                scale_st.set_value(st["volume"])
                scale_st.set_hexpand(True)
                scale_st.connect("value-changed", lambda s, s_id=st["id"]: AudioBackend.set_app_volume(s_id, s.get_value()))
                row.pack_start(scale_st, True, True, 0)

                btn_st_mute = Gtk.Button(label="󰝟" if st["muted"] else "󰕾")
                btn_st_mute.get_style_context().add_class("icon-btn")
                btn_st_mute.connect("clicked", lambda b, s_id=st["id"]: self._on_stream_mute_toggle(s_id, b))
                row.pack_start(btn_st_mute, False, False, 0)

                apps_card.pack_start(row, False, False, 2)
            content_box.pack_start(apps_card, False, False, 0)

    def _on_out_vol_changed(self, scale):
        val = int(scale.get_value())
        self.lbl_out_vol.set_text(f"{val}%")
        AudioBackend.set_master_volume(val)

    def _on_out_mute_toggle(self, btn):
        AudioBackend.toggle_master_mute()
        vol, muted = AudioBackend.get_master_volume()
        btn.set_label("󰝟" if muted else "󰕾")

    def _on_mic_vol_changed(self, scale):
        val = int(scale.get_value())
        self.lbl_mic_vol.set_text(f"{val}%")
        AudioBackend.set_mic_volume(val)

    def _on_mic_mute_toggle(self, btn):
        AudioBackend.toggle_mic_mute()
        vol, muted = AudioBackend.get_mic_volume()
        btn.set_label("󰍭" if muted else "󰍬")
        if muted:
            btn.get_style_context().add_class("active")
        else:
            btn.get_style_context().remove_class("active")

    def _on_sink_select(self, sink_id):
        AudioBackend.set_default_sink(sink_id)
        self.close()

    def _on_stream_mute_toggle(self, stream_id, btn):
        AudioBackend.toggle_app_mute(stream_id)
        # Update icon
        cur = btn.get_label()
        btn.set_label("󰕾" if cur == "󰝟" else "󰝟")

if __name__ == "__main__":
    app = AudioPopup()
    app.run()
