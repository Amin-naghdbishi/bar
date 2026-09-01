"""
Desktop and Papirus Icon Theme Lookup Resolver
Resolves application IDs to standard Linux desktop & Papirus icons
"""

import os
from pathlib import Path

# Complete Papirus-Dark Linux Desktop Icon Mapping
PAPIRUS_MAP = {
    # Web Browsers
    "firefox": "󰈹",
    "org.mozilla.firefox": "󰈹",
    "firefox-esr": "󰈹",
    "google-chrome": "",
    "google-chrome-stable": "",
    "chromium": "",
    "org.chromium.Chromium": "",
    "brave-browser": "󰖟",
    "brave": "󰖟",
    "microsoft-edge": "󰇩",
    "opera": "",
    "vivaldi": "󰖟",
    "tor-browser": "󰖟",

    # Terminals
    "alacritty": "",
    "kitty": "󰄛",
    "wezterm": "",
    "org.wezfurlong.wezterm": "",
    "foot": "",
    "gnome-terminal": "",
    "org.gnome.Terminal": "",
    "tilix": "",
    "konsole": "",
    "org.kde.konsole": "",
    "xterm": "",
    "urxvt": "",
    "terminator": "",
    "xfce4-terminal": "",
    "utilities-terminal": "",

    # File Managers
    "nautilus": "󰉋",
    "org.gnome.Nautilus": "󰉋",
    "thunar": "󰉋",
    "org.xfce.thunar": "󰉋",
    "dolphin": "󰉋",
    "org.kde.dolphin": "󰉋",
    "nemo": "󰉋",
    "pcmanfm": "󰉋",
    "system-file-manager": "󰉋",

    # Text Editors & IDEs
    "code": "󰨞",
    "visual-studio-code": "󰨞",
    "vscode": "󰨞",
    "vscodium": "󰨞",
    "gedit": "󰷈",
    "org.gnome.gedit": "󰷈",
    "kate": "󰷈",
    "org.kde.kate": "󰷈",
    "mousepad": "󰷈",
    "leafpad": "󰷈",
    "neovim": "",
    "nvim": "",
    "vim": "",
    "emacs": "",
    "sublime_text": "󰨞",
    "text-editor": "󰷈",

    # Messaging & Social
    "telegramdesktop": "",
    "org.telegram.desktop": "",
    "telegram-desktop": "",
    "telegram": "",
    "discord": "",
    "vesktop": "",
    "webcord": "",
    "element": "󰭹",
    "deltachat": "󰭹",
    "signal": "󰭹",
    "slack": "󰒱",

    # Media & Audio
    "spotify": "",
    "spotify-launcher": "",
    "vlc": "󰕼",
    "org.videolan.VLC": "󰕼",
    "mpv": "",
    "io.mpv.Mpv": "",
    "pavucontrol": "󰕾",
    "org.pulseaudio.pavucontrol": "󰕾",
    "obs": "󰐌",
    "com.obsproject.Studio": "󰐌",
    "audacity": "󰓃",

    # Graphics & Productivity
    "gimp": "",
    "org.gimp.GIMP": "",
    "inkscape": "",
    "org.inkscape.Inkscape": "",
    "blender": "󰂫",
    "org.blender.Blender": "󰂫",
    "libreoffice": "󰏆",
    "libreoffice-writer": "󰏆",
    "libreoffice-calc": "󰏆",
    "libreoffice-impress": "󰏆",
    "obsidian": "󱓧",
    "anki": "󰠮",
    "hiddify": "󰒄",
    "steam": "󰓓",
    "thunderbird": "󰇮",
    "org.mozilla.Thunderbird": "󰇮",

    # Settings & Utilities
    "gnome-control-center": "󰒓",
    "systemsettings": "󰒓",
    "settings": "󰒓",
    "preferences-system": "󰒓",
    "gnome-system-monitor": "󰍛",
    "btop": "󰍛",
    "htop": "󰍛",
    "gnome-calculator": "󰃬",
    "kcalc": "󰃬",
    "bitwarden": "󰞀",
    "default": "󰣆"
}

def resolve_icon_glyph(app_id):
    if not app_id:
        return PAPIRUS_MAP["default"]

    app_clean = app_id.lower().strip()
    
    # 1. Exact match
    if app_clean in PAPIRUS_MAP:
        return PAPIRUS_MAP[app_clean]

    # 2. Substring match
    for k, v in PAPIRUS_MAP.items():
        if k in app_clean or app_clean in k:
            return v

    # 3. Desktop Entry Lookup
    desktop_dirs = [
        Path.home() / ".local" / "share" / "applications",
        Path("/usr/share/applications")
    ]
    for d in desktop_dirs:
        if d.exists():
            for df in d.glob(f"*{app_clean}*.desktop"):
                try:
                    with open(df, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith("Icon="):
                                icon_name = line.split("=", 1)[1].strip().lower()
                                for k, v in PAPIRUS_MAP.items():
                                    if k in icon_name or icon_name in k:
                                        return v
                except Exception:
                    pass

    return PAPIRUS_MAP["default"]
