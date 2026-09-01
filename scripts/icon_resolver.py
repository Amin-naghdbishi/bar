#!/usr/bin/env python3
"""
Linux Desktop & Papirus Icon Theme Lookup Resolver
Implements strict Freedesktop & GTK Icon Theme Specification lookup:
1. Find application's .desktop file
2. Read the Icon= entry
3. Resolve the icon file using Papirus icon theme (First Priority)
4. Return absolute path to Papirus SVG/PNG icon file
"""

import glob
import os
import sys
from pathlib import Path

# XDG Desktop Application Directories
DESKTOP_DIRS = [
    Path.home() / ".local" / "share" / "applications",
    Path("/usr/share/applications"),
    Path("/usr/local/share/applications"),
    Path("/var/lib/flatpak/exports/share/applications"),
    Path.home() / ".local" / "share" / "flatpak" / "exports" / "share" / "applications",
    Path("/var/lib/snapd/desktop/applications")
]

# Papirus Icon Theme Search Directories (First Priority)
PAPIRUS_THEME_DIRS = [
    Path("/usr/share/icons/Papirus-Dark"),
    Path("/usr/share/icons/Papirus"),
    Path.home() / ".local" / "share" / "icons" / "Papirus-Dark",
    Path.home() / ".local" / "share" / "icons" / "Papirus",
    Path.home() / ".icons" / "Papirus-Dark",
    Path.home() / ".icons" / "Papirus",
    Path("/usr/local/share/icons/Papirus-Dark"),
    Path("/usr/local/share/icons/Papirus"),
    Path.home() / ".config" / "niri-panel" / "assets" / "icons" / "Papirus-Dark",
    Path.home() / ".config" / "niri-panel" / "assets" / "icons" / "Papirus",
    Path(__file__).resolve().parent.parent / "assets" / "icons" / "Papirus-Dark",
    Path(__file__).resolve().parent.parent / "assets" / "icons" / "Papirus"
]

# Secondary/Fallback GTK Theme Directories
FALLBACK_THEME_DIRS = [
    Path("/usr/share/icons/hicolor"),
    Path("/usr/share/icons/Adwaita"),
    Path("/usr/share/pixmaps"),
    Path("/usr/share/icons")
]

def find_desktop_file(app_id):
    """
    Finds the .desktop file matching the app_id.
    """
    if not app_id:
        return None
    
    app_clean = app_id.lower().strip()
    
    for d in DESKTOP_DIRS:
        if not d.exists():
            continue
            
        # 1. Exact name matches
        for ext in [".desktop"]:
            direct = d / f"{app_id}{ext}"
            if direct.exists():
                return direct
            direct_lower = d / f"{app_clean}{ext}"
            if direct_lower.exists():
                return direct_lower
                
        # 2. Pattern matches (e.g. org.mozilla.firefox.desktop)
        matches = list(d.glob(f"*{app_clean}*.desktop"))
        if matches:
            # Sort by shortest filename length to prefer direct matches
            matches.sort(key=lambda p: len(p.name))
            return matches[0]
            
    return None

def extract_icon_name_from_desktop(desktop_file_path):
    """
    Reads the Icon= entry from a .desktop file.
    """
    if not desktop_file_path or not os.path.exists(desktop_file_path):
        return None
    try:
        with open(desktop_file_path, "r", encoding="utf-8", errors="ignore") as f:
            in_desktop_entry = False
            for line in f:
                line = line.strip()
                if line == "[Desktop Entry]":
                    in_desktop_entry = True
                    continue
                elif line.startswith("[") and line.endswith("]"):
                    in_desktop_entry = False
                    
                if in_desktop_entry and line.startswith("Icon="):
                    icon_val = line.split("=", 1)[1].strip()
                    if icon_val:
                        return icon_val
    except Exception:
        pass
    return None

def search_theme_for_icon(theme_dir, icon_names):
    """
    Searches a theme directory hierarchy for an icon matching any of the icon_names.
    Prioritizes SVG and 48x48/scalable sizes.
    """
    if not theme_dir.exists():
        return None
        
    for name in icon_names:
        # If absolute path was given in .desktop file
        if os.path.isabs(name) and os.path.exists(name):
            return Path(name)
            
        # Subdirectories in Papirus: 48x48/apps, 32x32/apps, 24x24/apps, scalable/apps, etc.
        patterns = [
            f"48x48/apps/{name}.svg",
            f"48x48/apps/{name}.png",
            f"scalable/apps/{name}.svg",
            f"32x32/apps/{name}.svg",
            f"24x24/apps/{name}.svg",
            f"**/{name}.svg",
            f"**/{name}.png",
            f"**/{name}-*.svg",
            f"**/{name}-*.png",
            f"*{name}*.svg"
        ]
        for pat in patterns:
            matches = list(theme_dir.glob(pat))
            if matches:
                # Prioritize 48x48 or scalable
                matches.sort(key=lambda p: 0 if "48x48" in str(p) or "scalable" in str(p) else 1)
                return matches[0]
                
    return None

def resolve_app_icon_path(app_id):
    """
    Resolves the exact Papirus icon path for a given application ID:
    1. Finds .desktop file
    2. Reads Icon= value
    3. Searches Papirus icon theme (first priority)
    4. Searches fallback GTK icon themes
    """
    if not app_id:
        return None
        
    app_clean = app_id.lower().strip()
    candidate_names = [app_id, app_clean]
    
    # Common standard Papirus icon names
    common_map = {
        "firefox": "firefox",
        "alacritty": "utilities-terminal",
        "kitty": "utilities-terminal",
        "wezterm": "utilities-terminal",
        "foot": "utilities-terminal",
        "terminal": "utilities-terminal",
        "nautilus": "system-file-manager",
        "thunar": "system-file-manager",
        "dolphin": "system-file-manager",
        "files": "system-file-manager",
        "code": "visual-studio-code",
        "vscode": "visual-studio-code",
        "vscodium": "visual-studio-code",
        "gedit": "text-editor",
        "kate": "text-editor",
        "mousepad": "text-editor",
        "editor": "text-editor",
        "telegramdesktop": "telegram",
        "telegram-desktop": "telegram",
        "telegram": "telegram",
        "discord": "discord",
        "spotify": "spotify",
        "settings": "preferences-system"
    }
    if app_clean in common_map:
        candidate_names.insert(0, common_map[app_clean])

    # 1. Desktop File Lookup
    df = find_desktop_file(app_id)
    if df:
        icon_from_df = extract_icon_name_from_desktop(df)
        if icon_from_df and icon_from_df not in candidate_names:
            candidate_names.insert(0, icon_from_df)
            candidate_names.insert(1, icon_from_df.lower())

    # 2. Resolve via Papirus Theme Dirs (Priority 1)
    for theme_dir in PAPIRUS_THEME_DIRS:
        found = search_theme_for_icon(theme_dir, candidate_names)
        if found and found.exists():
            return found.resolve()

    # 3. Resolve via Fallback Themes
    for theme_dir in FALLBACK_THEME_DIRS:
        found = search_theme_for_icon(theme_dir, candidate_names)
        if found and found.exists():
            return found.resolve()

    return None

def resolve_app_icon_markup(app_id):
    """
    Returns the Pango image markup for Waybar taskbar buttons.
    """
    icon_path = resolve_app_icon_path(app_id)
    if icon_path:
        return f"<img src='{icon_path}' width='20' height='20'/>"
        
    return "<span font='15'>󰣆</span>"

def run_diagnostic_test():
    test_apps = [
        ("Firefox", "firefox"),
        ("Terminal", "alacritty"),
        ("File Manager", "nautilus"),
        ("Telegram", "telegramdesktop"),
        ("Text Editor", "code"),
        ("Discord", "discord"),
        ("Spotify", "spotify")
    ]
    print("=================================================================")
    print("           Papirus Desktop Icon Resolution Diagnostic            ")
    print("=================================================================")
    all_passed = True
    for name, app_id in test_apps:
        df = find_desktop_file(app_id)
        icon_val = extract_icon_name_from_desktop(df) if df else "N/A"
        resolved_path = resolve_app_icon_path(app_id)
        
        is_papirus = resolved_path and "Papirus" in str(resolved_path)
        status = "✓ OK" if is_papirus else "✗ FAILED"
        if not is_papirus:
            all_passed = False
            
        print(f"[{status}] {name:15} (app_id: {app_id})")
        print(f"       .desktop file: {str(df)}")
        print(f"       Icon= entry:   {icon_val}")
        print(f"       Resolved Path: {str(resolved_path)}")
        print("-----------------------------------------------------------------")
        
    return all_passed

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["--test", "-t", "--debug"]:
            success = run_diagnostic_test()
            sys.exit(0 if success else 1)
        else:
            resolved = resolve_app_icon_path(arg)
            print(f"{arg} → {resolved}")
    else:
        run_diagnostic_test()
