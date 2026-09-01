#!/usr/bin/env python3
"""
Niri Dynamic Application Taskbar for Waybar
- Groups multiple windows under a single application icon
- Shows small subtle dots underneath for open windows (●, ● ●, ● ● ●)
- Highlights active window dot
- Resolves proper Papirus application icons
- Left click: Focus window or open Window Grouping Selector Popup
- Right click: Application Context Menu Popup
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

CONFIG_DIRS = [
    Path.home() / ".config" / "niri-panel",
    Path(__file__).resolve().parent.parent / "config",
    Path.cwd() / "config"
]

DEFAULT_PINNED = [
    {"name": "Firefox", "app_id": "firefox", "icon": "firefox", "exec": "firefox", "autostart": False},
    {"name": "Terminal", "app_id": "alacritty", "icon": "utilities-terminal", "exec": "alacritty", "autostart": False},
    {"name": "Files", "app_id": "nautilus", "icon": "system-file-manager", "exec": "nautilus", "autostart": False},
    {"name": "Editor", "app_id": "code", "icon": "visual-studio-code", "exec": "code", "autostart": False}
]

ICON_MAP = {
    "firefox": "󰈹",
    "org.mozilla.firefox": "󰈹",
    "google-chrome": "",
    "chromium": "",
    "brave-browser": "󰖟",
    "brave": "󰖟",
    "alacritty": "",
    "kitty": "󰄛",
    "wezterm": "",
    "org.wezfurlong.wezterm": "",
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
    "vlc": "󰕼",
    "hiddify": "󰒄",
    "anki": "󰠮",
    "pavucontrol": "󰕾",
    "settings": "󰒓",
    "gnome-control-center": "󰒓",
    "default": "󰣆"
}

def get_config_file(filename):
    for d in CONFIG_DIRS:
        p = d / filename
        if p.exists():
            return p
    p = Path.home() / ".config" / "niri-panel" / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def load_pinned():
    p = get_config_file("pinned.json")
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return list(DEFAULT_PINNED)

def get_niri_windows():
    try:
        proc = subprocess.run(
            ["niri", "msg", "-j", "windows"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "windows" in data:
                return data["windows"]
    except Exception:
        pass
    return []

def get_icon_glyph(app_id):
    if not app_id:
        return ICON_MAP["default"]
    app_id_lower = app_id.lower()
    for k, v in ICON_MAP.items():
        if k in app_id_lower:
            return v
    return ICON_MAP["default"]

def build_taskbar_state():
    pinned_apps = load_pinned()
    running_windows = get_niri_windows()
    
    grouped_windows = {}
    for win in running_windows:
        app_id = (win.get("app_id") or win.get("appId") or "unknown").lower()
        if app_id not in grouped_windows:
            grouped_windows[app_id] = []
        grouped_windows[app_id].append(win)
        
    apps = []
    seen_app_ids = set()

    # 1. Pinned Apps
    for pin in pinned_apps:
        app_id = pin.get("app_id", "").lower()
        seen_app_ids.add(app_id)
        
        windows = grouped_windows.get(app_id, [])
        if not windows:
            for k, wins in grouped_windows.items():
                if k == app_id or app_id in k or k in app_id:
                    windows = wins
                    seen_app_ids.add(k)
                    break
                    
        is_running = len(windows) > 0
        is_active = any(w.get("is_focused") for w in windows)
        
        apps.append({
            "name": pin.get("name", app_id),
            "app_id": app_id,
            "exec": pin.get("exec", app_id),
            "is_pinned": True,
            "is_running": is_running,
            "is_active": is_active,
            "window_count": len(windows),
            "windows": windows,
            "glyph": get_icon_glyph(app_id)
        })

    # 2. Running unpinned apps
    for app_id, windows in grouped_windows.items():
        if app_id in seen_app_ids:
            continue
        is_active = any(w.get("is_focused") for w in windows)
        name = app_id.capitalize()
        if windows and windows[0].get("title"):
            title = windows[0].get("title")
            if len(title) > 20:
                title = title[:18] + "…"
            name = title
            
        apps.append({
            "name": name,
            "app_id": app_id,
            "exec": app_id,
            "is_pinned": False,
            "is_running": True,
            "is_active": is_active,
            "window_count": len(windows),
            "windows": windows,
            "glyph": get_icon_glyph(app_id)
        })

    return apps

def format_dots(count, is_active):
    if count <= 0:
        return ""
    
    dots_markup = []
    for i in range(count):
        if is_active and i == 0:
            # Active window dot is illuminated sky-blue
            dots_markup.append("<span color='#38bdf8'>●</span>")
        else:
            # Running window dot is neutral white/slate
            dots_markup.append("<span color='#94a3b8'>●</span>")
    
    dots_str = " ".join(dots_markup)
    return f" <span font='7' rise='-2000'>{dots_str}</span>"

def format_waybar_taskbar():
    apps = build_taskbar_state()
    items = []
    
    for a in apps:
        glyph = a["glyph"]
        dots = format_dots(a["window_count"], a["is_active"]) if a["is_running"] else ""
        
        if a["is_active"]:
            item_markup = f"<span color='#ffffff' font='15'>{glyph}</span>{dots}"
        elif a["is_running"]:
            item_markup = f"<span color='#cbd5e1' font='15'>{glyph}</span>{dots}"
        else:
            # Pinned only
            item_markup = f"<span color='#64748b' font='15'>{glyph}</span>"
            
        items.append(item_markup)

    text_repr = "    ".join(items) if items else "󰣆"
    
    return json.dumps({
        "text": text_repr,
        "alt": "taskbar",
        "tooltip": False,
        "class": ["taskbar-container"]
    })

def handle_click(app_id_or_index=None):
    apps = build_taskbar_state()
    if not apps:
        return
    
    target_app = None
    if app_id_or_index:
        try:
            idx = int(app_id_or_index)
            if 0 <= idx < len(apps):
                target_app = apps[idx]
        except ValueError:
            for a in apps:
                if a["app_id"] == app_id_or_index or a["name"].lower() == app_id_or_index.lower():
                    target_app = a
                    break
    if not target_app and apps:
        target_app = next((a for a in apps if a["is_active"]), apps[0])

    if not target_app:
        return

    # Scenario 1: Closed -> Launch
    if not target_app["is_running"]:
        exec_cmd = target_app["exec"]
        subprocess.Popen(exec_cmd, shell=True)
        return

    # Scenario 2: Single Window -> Focus
    if target_app["window_count"] == 1:
        win_id = target_app["windows"][0].get("id")
        if win_id is not None:
            subprocess.run(["niri", "msg", "action", "focus-window", "--id", str(win_id)])
        return

    # Scenario 3: Multiple Windows -> Open real Window Grouping Selector Popup
    script_dir = Path(__file__).resolve().parent
    window_menu_py = script_dir.parent / "popup" / "taskbar" / "window_menu.py"
    if not window_menu_py.exists():
        window_menu_py = Path.home() / ".config" / "niri-panel" / "popup" / "taskbar" / "window_menu.py"
        
    if window_menu_py.exists():
        subprocess.Popen([sys.executable, str(window_menu_py), "--app", target_app["app_id"]])
    else:
        win_id = target_app["windows"][0].get("id")
        if win_id is not None:
            subprocess.run(["niri", "msg", "action", "focus-window", "--id", str(win_id)])

def handle_right_click(app_id_or_index=None):
    apps = build_taskbar_state()
    if not apps:
        return
    target_app = None
    if app_id_or_index:
        try:
            idx = int(app_id_or_index)
            if 0 <= idx < len(apps):
                target_app = apps[idx]
        except ValueError:
            for a in apps:
                if a["app_id"] == app_id_or_index or a["name"].lower() == app_id_or_index.lower():
                    target_app = a
                    break
    if not target_app and apps:
        target_app = next((a for a in apps if a["is_active"]), apps[0])
    
    if not target_app:
        return

    script_dir = Path(__file__).resolve().parent
    context_menu_py = script_dir.parent / "popup" / "taskbar" / "context_menu.py"
    if not context_menu_py.exists():
        context_menu_py = Path.home() / ".config" / "niri-panel" / "popup" / "taskbar" / "context_menu.py"

    if context_menu_py.exists():
        subprocess.Popen([
            sys.executable,
            str(context_menu_py),
            "--app", target_app["app_id"],
            "--name", target_app["name"],
            "--exec", target_app["exec"],
            "--pinned", "1" if target_app["is_pinned"] else "0",
            "--running", "1" if target_app["is_running"] else "0"
        ])

def stream_taskbar():
    prev_output = ""
    while True:
        curr_output = format_waybar_taskbar()
        if curr_output != prev_output:
            print(curr_output, flush=True)
            prev_output = curr_output
        time.sleep(0.4)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--watch":
            stream_taskbar()
        elif cmd == "--click":
            arg = sys.argv[2] if len(sys.argv) > 2 else None
            handle_click(arg)
        elif cmd == "--right-click":
            arg = sys.argv[2] if len(sys.argv) > 2 else None
            handle_right_click(arg)
        elif cmd == "--json":
            print(json.dumps(build_taskbar_state(), indent=2))
        else:
            print(format_waybar_taskbar())
    else:
        print(format_waybar_taskbar())
