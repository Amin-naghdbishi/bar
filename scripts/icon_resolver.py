"""
High Performance Desktop & Papirus Icon Lookup Engine
- Fast O(1) in-memory cached lookup
- Resolves application IDs to authentic Papirus-style application icons
- Zero disk rescanning on subsequent queries
"""

import os
from pathlib import Path

# In-Memory Cache for O(1) Instant Resolution
_ICON_CACHE = {}

PAPIRUS_APP_ICONS = {
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
    "audacity": "󰓃",
    "obs": "󰐌",
    "com.obsproject.Studio": "󰐌",

    # Graphics & Productivity
    "gimp": "",
    "org.gimp.GIMP": "",
    "inkscape": "",
    "org.inkscape.Inkscape": "",
    "blender": "󰂫",
    "org.blender.Blender": "󰂫",
    "libreoffice": "󰏆",
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
    "default": "󰣆"
}

DESKTOP_DIRS = [
    Path.home() / ".local" / "share" / "applications",
    Path("/usr/share/applications"),
    Path("/usr/local/share/applications")
]

def resolve_app_icon(app_id):
    """
    Resolves application icon glyph with instant O(1) in-memory caching.
    """
    if not app_id:
        return PAPIRUS_APP_ICONS["default"]

    app_clean = app_id.lower().strip()

    # 1. Fast Cache Hit
    if app_clean in _ICON_CACHE:
        return _ICON_CACHE[app_clean]

    # 2. Exact Match in Papirus Icons Map
    if app_clean in PAPIRUS_APP_ICONS:
        icon = PAPIRUS_APP_ICONS[app_clean]
        _ICON_CACHE[app_clean] = icon
        return icon

    # 3. Substring match
    for k, v in PAPIRUS_APP_ICONS.items():
        if k in app_clean or app_clean in k:
            _ICON_CACHE[app_clean] = v
            return v

    # 4. Desktop Entry Resolution (only executed once per unknown app)
    for d in DESKTOP_DIRS:
        if d.exists():
            for df in d.glob(f"*{app_clean}*.desktop"):
                try:
                    with open(df, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith("Icon="):
                                icon_name = line.split("=", 1)[1].strip().lower()
                                for k, v in PAPIRUS_APP_ICONS.items():
                                    if k in icon_name:
                                        _ICON_CACHE[app_clean] = v
                                        return v
                except Exception:
                    pass

    default_icon = PAPIRUS_APP_ICONS["default"]
    _ICON_CACHE[app_clean] = default_icon
    return default_icon
