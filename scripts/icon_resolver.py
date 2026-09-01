"""
Desktop & Papirus Icon Resolver
Resolves application IDs to standard Linux desktop & Papirus icons
"""

import os
import glob
from pathlib import Path

PAPIRUS_GLYPHS = {
    "firefox": "󰈹",
    "org.mozilla.firefox": "󰈹",
    "google-chrome": "",
    "chromium": "",
    "brave-browser": "󰖟",
    "brave": "󰖟",
    "microsoft-edge": "󰇩",
    "opera": "",
    "alacritty": "",
    "kitty": "󰄛",
    "org.wezfurlong.wezterm": "",
    "wezterm": "",
    "foot": "",
    "gnome-terminal": "",
    "tilix": "",
    "konsole": "",
    "xterm": "",
    "nautilus": "󰉋",
    "org.gnome.Nautilus": "󰉋",
    "thunar": "󰉋",
    "dolphin": "󰉋",
    "nemo": "󰉋",
    "pcmanfm": "󰉋",
    "code": "󰨞",
    "visual-studio-code": "󰨞",
    "vscodium": "󰨞",
    "gedit": "󰷈",
    "kate": "󰷈",
    "mousepad": "󰷈",
    "neovim": "",
    "nvim": "",
    "telegramdesktop": "",
    "org.telegram.desktop": "",
    "telegram-desktop": "",
    "discord": "",
    "vesktop": "",
    "spotify": "",
    "spotify-launcher": "",
    "obsidian": "󱓧",
    "steam": "󰓓",
    "gimp": "",
    "org.gimp.GIMP": "",
    "inkscape": "",
    "blender": "󰂫",
    "mpv": "",
    "io.mpv.Mpv": "",
    "vlc": "󰕼",
    "obs": "󰐌",
    "hiddify": "󰒄",
    "anki": "󰠮",
    "pavucontrol": "󰕾",
    "settings": "󰒓",
    "gnome-control-center": "󰒓",
    "systemsettings": "󰒓",
    "thunderbird": "󰇮",
    "libreoffice": "󰏆",
    "default": "󰣆"
}

def resolve_icon_glyph(app_id):
    if not app_id:
        return PAPIRUS_GLYPHS["default"]
    
    app_lower = app_id.lower()
    for k, v in PAPIRUS_GLYPHS.items():
        if k in app_lower:
            return v
            
    # Try finding .desktop file to resolve icon name
    desktop_dirs = [
        Path.home() / ".local" / "share" / "applications",
        Path("/usr/share/applications")
    ]
    for d in desktop_dirs:
        if d.exists():
            for df in d.glob(f"*{app_lower}*.desktop"):
                try:
                    with open(df, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith("Icon="):
                                icon_name = line.split("=", 1)[1].strip().lower()
                                for k, v in PAPIRUS_GLYPHS.items():
                                    if k in icon_name:
                                        return v
                except Exception:
                    pass
                    
    return PAPIRUS_GLYPHS["default"]
