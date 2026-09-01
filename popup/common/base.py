"""
Base Popup Window Class for Niri Desktop Shell
Provides:
- Layer Shell integration (anchored to taskbar)
- Translucent RGBA backdrop & Glass styling
- Close on click-outside and Escape key
- Singleton PID toggle management
- Reusable UI builder helpers
"""

import os
import signal
import sys
from pathlib import Path

# Check if GUI is possible
HAS_GI = False
try:
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gtk, Gdk, GLib, Gio
    HAS_GI = True
    
    # Try layer shell
    try:
        gi.require_version('GtkLayerShell', '0.1')
        from gi.repository import GtkLayerShell
        HAS_LAYER_SHELL = True
    except Exception:
        HAS_LAYER_SHELL = False
except Exception:
    HAS_GI = False
    HAS_LAYER_SHELL = False

class BasePopupWindow:
    def __init__(self, title="Popup", width=360, height=None, anchor="right", name="popup"):
        if not HAS_GI:
            print(f"[Niri-Panel] Gtk3 not available. Cannot render GUI for {title}.")
            return

        self.name = name
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title(title)
        self.window.set_wmclass("niri-panel-popup", "niri-panel-popup")
        self.window.set_role("popup")
        self.window.set_decorated(False)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_app_paintable(True)
        self.window.get_style_context().add_class("popup-window")

        if width:
            self.window.set_default_size(width, height or -1)

        # Translucent RGBA visual
        screen = self.window.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.window.set_visual(visual)

        # Apply Layer Shell if available
        if HAS_LAYER_SHELL:
            GtkLayerShell.init_for_window(self.window)
            GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.TOP)
            GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.BOTTOM, True)
            GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.BOTTOM, 52)
            
            if anchor == "right":
                GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, True)
                GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.RIGHT, 14)
            elif anchor == "left":
                GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, True)
                GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.LEFT, 14)
            elif anchor == "center":
                # Center horizontally
                GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, False)
                GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, False)
                
            GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.ON_DEMAND)
        else:
            self.window.set_position(Gtk.WindowPosition.CENTER)

        # Load Unified CSS
        self._load_css()

        # Keyboard & focus signals
        self.window.connect("key-press-event", self._on_key_press)
        self.window.connect("focus-out-event", self._on_focus_out)
        self.window.connect("destroy", self._on_destroy)

        # Main container
        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.root_box.get_style_context().add_class("popup-root")
        self.window.add(self.root_box)

    def _load_css(self):
        css_file = Path(__file__).resolve().parent / "styles.css"
        if css_file.exists():
            css_provider = Gtk.CssProvider()
            css_provider.load_from_path(str(css_file))
            Gtk.StyleContext.add_provider_for_screen(
                self.window.get_screen(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _on_key_press(self, widget, event):
        # Escape key closes popup
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def _on_focus_out(self, widget, event):
        # Auto-dismiss on click outside
        self.close()
        return False

    def _on_destroy(self, widget):
        Gtk.main_quit()

    def close(self):
        if HAS_GI and self.window:
            self.window.destroy()

    def create_header(self, title_text, subtitle_text="", icon_glyph=""):
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.get_style_context().add_class("popup-header")

        if icon_glyph:
            icon_lbl = Gtk.Label()
            icon_lbl.set_markup(f"<span size='large' color='#38bdf8'>{icon_glyph}</span>")
            header_box.pack_start(icon_lbl, False, False, 0)

        title_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        lbl_title = Gtk.Label()
        lbl_title.set_markup(f"<b>{title_text}</b>")
        lbl_title.set_xalign(0)
        lbl_title.get_style_context().add_class("popup-title")
        title_vbox.pack_start(lbl_title, False, False, 0)

        if subtitle_text:
            lbl_sub = Gtk.Label(label=subtitle_text)
            lbl_sub.set_xalign(0)
            lbl_sub.get_style_context().add_class("popup-subtitle")
            title_vbox.pack_start(lbl_sub, False, False, 0)

        header_box.pack_start(title_vbox, True, True, 0)

        # Close button
        btn_close = Gtk.Button(label="✕")
        btn_close.get_style_context().add_class("popup-close-btn")
        btn_close.connect("clicked", lambda b: self.close())
        header_box.pack_end(btn_close, False, False, 0)

        return header_box

    def create_card(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.get_style_context().add_class("popup-card")
        return box

    def create_section_title(self, text):
        lbl = Gtk.Label(label=text)
        lbl.set_xalign(0)
        lbl.get_style_context().add_class("section-title")
        return lbl

    def run(self):
        if HAS_GI:
            self.window.show_all()
            Gtk.main()
