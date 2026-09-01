"""
Desktop and Papirus Icon Theme Lookup Resolver
Strictly resolves application icons using Linux Desktop Icon Theme System:
1. Desktop entry (.desktop) Icon= lookup
2. Papirus / Papirus-Dark icon theme lookup (/usr/share/icons/Papirus*, ~/.icons/Papirus*)
3. Bundled Papirus assets lookup (~/.config/niri-panel/assets/icons/apps)
4. Other installed GTK icon themes
"""

import os
import glob
from pathlib import Path

BUNDLED_DIRS = [
    Path.home() / ".config" / "niri-panel" / "assets" / "icons" / "apps",
    Path(__file__).resolve().parent.parent / "assets" / "icons" / "apps",
    Path.cwd() / "assets" / "icons" / "apps"
]

PAPIRUS_THEME_DIRS = [
    Path("/usr/share/icons/Papirus-Dark"),
    Path("/usr/share/icons/Papirus"),
    Path.home() / ".local" / "share" / "icons" / "Papirus-Dark",
    Path.home() / ".local" / "share" / "icons" / "Papirus",
    Path.home() / ".icons" / "Papirus-Dark",
    Path.home() / ".icons" / "Papirus"
]

FALLBACK_THEME_DIRS = [
    Path("/usr/share/icons/hicolor"),
    Path("/usr/share/pixmaps"),
    Path("/usr/share/icons")
]

# Common name mappings for desktop apps to Papirus icon file names
APP_TO_ICON_NAME = {
    "firefox": "firefox",
    "org.mozilla.firefox": "firefox",
    "firefox-esr": "firefox",
    "google-chrome": "google-chrome",
    "google-chrome-stable": "google-chrome",
    "chromium": "chromium",
    "org.chromium.Chromium": "chromium",
    "brave-browser": "brave-browser",
    "brave": "brave",
    "microsoft-edge": "microsoft-edge",
    "opera": "opera",
    "alacritty": "Alacritty",
    "kitty": "kitty",
    "wezterm": "org.wezfurlong.wezterm",
    "org.wezfurlong.wezterm": "org.wezfurlong.wezterm",
    "foot": "foot",
    "gnome-terminal": "org.gnome.Terminal",
    "org.gnome.Terminal": "org.gnome.Terminal",
    "tilix": "com.gexperts.Tilix",
    "konsole": "org.kde.konsole",
    "xterm": "xterm",
    "nautilus": "org.gnome.Nautilus",
    "org.gnome.Nautilus": "org.gnome.Nautilus",
    "thunar": "org.xfce.thunar",
    "dolphin": "org.kde.dolphin",
    "nemo": "nemo",
    "pcmanfm": "pcmanfm",
    "code": "visual-studio-code",
    "visual-studio-code": "visual-studio-code",
    "vscode": "visual-studio-code",
    "vscodium": "vscodium",
    "gedit": "org.gnome.gedit",
    "org.gnome.gedit": "org.gnome.gedit",
    "kate": "org.kde.kate",
    "mousepad": "org.xfce.mousepad",
    "telegramdesktop": "telegram",
    "org.telegram.desktop": "telegram",
    "telegram-desktop": "telegram",
    "telegram": "telegram",
    "discord": "discord",
    "vesktop": "discord",
    "spotify": "spotify",
    "spotify-launcher": "spotify",
    "steam": "steam",
    "gimp": "gimp",
    "org.gimp.GIMP": "gimp",
    "inkscape": "org.inkscape.Inkscape",
    "blender": "blender",
    "vlc": "vlc",
    "mpv": "mpv",
    "obs": "com.obsproject.Studio",
    "obsidian": "obsidian",
    "anki": "anki",
    "hiddify": "hiddify",
    "settings": "preferences-system",
    "gnome-control-center": "gnome-control-center"
}

def find_icon_in_theme_dir(theme_dir, icon_names):
    if not theme_dir.exists():
        return None
    for name in icon_names:
        patterns = [
            f"**/{name}.svg",
            f"**/{name}.png",
            f"**/{name}-*.svg",
            f"**/{name}-*.png",
            f"*{name}*.svg"
        ]
        for pat in patterns:
            matches = list(theme_dir.glob(pat))
            if matches:
                matches.sort(key=lambda p: 0 if "48" in str(p) or "scalable" in str(p) else 1)
                return matches[0]
    return None

def resolve_desktop_icon_file(app_id):
    if not app_id:
        return None
    
    app_clean = app_id.lower().strip()
    candidate_names = [app_id, app_clean]
    
    mapped_name = APP_TO_ICON_NAME.get(app_clean)
    if mapped_name:
        candidate_names.insert(0, mapped_name)

    # Check .desktop files for Icon=
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
                                icon_val = line.split("=", 1)[1].strip()
                                if icon_val and icon_val not in candidate_names:
                                    candidate_names.insert(0, icon_val)
                                    candidate_names.insert(1, icon_val.lower())
                except Exception:
                    pass

    # 1. Look in Papirus Theme Dirs
    for pt in PAPIRUS_THEME_DIRS:
        found = find_icon_in_theme_dir(pt, candidate_names)
        if found:
            return found

    # 2. Look in Bundled Papirus Assets
    for bd in BUNDLED_DIRS:
        if bd.exists():
            for name in candidate_names:
                for ext in [".svg", ".png"]:
                    p = bd / f"{name}{ext}"
                    if p.exists():
                        return p
                if "fire" in name and (bd / "firefox.svg").exists():
                    return bd / "firefox.svg"
                if ("term" in name or "alacritty" in name or "kitty" in name) and (bd / "terminal.svg").exists():
                    return bd / "terminal.svg"
                if ("file" in name or "nautilus" in name or "thunar" in name) and (bd / "files.svg").exists():
                    return bd / "files.svg"
                if ("code" in name or "edit" in name or "kate" in name) and (bd / "code.svg").exists():
                    return bd / "code.svg"
                if "tele" in name and (bd / "telegram.svg").exists():
                    return bd / "telegram.svg"
                if "disc" in name and (bd / "discord.svg").exists():
                    return bd / "discord.svg"
                if "spot" in name and (bd / "spotify.svg").exists():
                    return bd / "spotify.svg"

    # 3. Look in Fallback Theme Dirs
    for ft in FALLBACK_THEME_DIRS:
        found = find_icon_in_theme_dir(ft, candidate_names)
        if found:
            return found

    return None

def resolve_app_icon_markup(app_id):
    """
    Returns Pango image markup for the Papirus application icon.
    """
    icon_file = resolve_desktop_icon_file(app_id)
    if icon_file and icon_file.exists():
        return f"<img src='{icon_file.resolve()}' width='20' height='20'/>"

    glyph_map = {
        "firefox": "󰈹", "terminal": "", "alacritty": "", "kitty": "󰄛",
        "files": "󰉋", "nautilus": "󰉋", "thunar": "󰉋",
        "code": "󰨞", "gedit": "󰷈", "telegram": "", "discord": "",
        "spotify": "", "steam": "󰓓"
    }
    app_lower = (app_id or "").lower()
    for k, v in glyph_map.items():
        if k in app_lower:
            return f"<span font='15'>{v}</span>"
            
    return "<span font='15'>󰣆</span>"
