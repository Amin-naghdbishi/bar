"""
Base Popup Window Class for Niri Desktop Shell
Creates a real independent Wayland floating surface window using GTK3 & gtk-layer-shell
"""

import os
import signal
import sys
from pathlib import Path

HAS_GI = False
HAS_LAYER_SHELL = False

try:
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gtk, Gdk, GLib, Gio
    HAS_GI = True
    
    try:
        gi.require_version('GtkLayerShell', '0.1')
        from gi.repository import GtkLayerShell
        HAS_LAYER_SHELL = True
    except Exception:
        HAS_LAYER_SHELL = False
except Exception as e:
    HAS_GI = False
    HAS_LAYER_SHELL = False

class BasePopupWindow:
    def __init__(self, title="Popup", width=360, height=None, anchor="right", name="popup"):
        self.name = name
        self.title = title
        self.width = width
        self.height = height
        self.anchor = anchor

        if not HAS_GI:
            print(f"[Niri-Panel Popup] Error: PyGObject (Gtk 3.0) is required to display the {title} window.")
            return

        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title(title)
        self.window.set_wmclass("niri-panel-popup", "niri-panel-popup")
        self.window.set_role("popup")
        self.window.set_decorated(False)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_app_paintable(True)
        self.window.set_keep_above(True)
        self.window.get_style_context().add_class("popup-window")

        if width:
            self.window.set_default_size(width, height or -1)

        # Translucent RGBA visual for frosted glass effect
        screen = self.window.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.window.set_visual(visual)

        # Layer Shell Positioning
        if HAS_LAYER_SHELL:
            GtkLayerShell.init_for_window(self.window)
            GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.TOP)
            GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.BOTTOM, True)
            GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.BOTTOM, 50)
            
            if anchor == "right":
                GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, True)
                GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.RIGHT, 12)
            elif anchor == "left":
                GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, True)
                GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.LEFT, 12)
            elif anchor == "center":
                GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, False)
                GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, False)
                
            GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.ON_DEMAND)
        else:
            # Fallback positioning
            self.window.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)
            self.window.set_position(Gtk.WindowPosition.CENTER)

        # Load Unified CSS stylesheet
        self._load_css()

        # Dismissal events (Escape key & click-outside)
        self.window.connect("key-press-event", self._on_key_press)
        self.window.connect("focus-out-event", self._on_focus_out)
        self.window.connect("destroy", self._on_destroy)

        # Main root container
        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.root_box.get_style_context().add_class("popup-root")
        self.window.add(self.root_box)

    def _load_css(self):
        css_paths = [
            Path(__file__).resolve().parent / "styles.css",
            Path.home() / ".config" / "niri-panel" / "popup" / "common" / "styles.css"
        ]
        for cp in css_paths:
            if cp.exists():
                try:
                    css_provider = Gtk.CssProvider()
                    css_provider.load_from_path(str(cp))
                    Gtk.StyleContext.add_provider_for_screen(
                        self.window.get_screen(),
                        css_provider,
                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                    )
                    break
                except Exception:
                    pass

    def _on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def _on_focus_out(self, widget, event):
        self.close()
        return False

    def _on_destroy(self, widget):
        Gtk.main_quit()

    def close(self):
        if HAS_GI and hasattr(self, "window") and self.window:
            self.window.destroy()

    def create_header(self, title_text, subtitle_text="", icon_glyph=""):
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.get_style_context().add_class("popup-header")

        if icon_glyph:
            icon_lbl = Gtk.Label()
            icon_lbl.set_markup(f"<span font='14' color='#38bdf8'>{icon_glyph}</span>")
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
        if HAS_GI and hasattr(self, "window") and self.window:
            self.window.show_all()
            Gtk.main()
