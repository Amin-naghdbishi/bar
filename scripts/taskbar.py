#!/usr/bin/env python3
"""
Niri Dynamic Application Taskbar for Waybar
Handles:
- Pinned applications (always shown)
- Running applications (detected via Niri IPC)
- Multi-window grouping with dot indicators (●, ● ●, ● ● ●)
- Active window state tracking
- Left click (Launch / Focus / Group Selector)
- Right click (Context menu: New window, Close, Pin/Unpin, Autostart, Quit)
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Paths to config
CONFIG_DIRS = [
    Path.home() / ".config" / "niri-panel",
    Path(__file__).resolve().parent.parent / "config"
]

DEFAULT_PINNED = [
    {"name": "Firefox", "app_id": "firefox", "icon": "firefox", "exec": "firefox", "autostart": false if False else False},
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
    "alacritty": "",
    "kitty": "󰄛",
    "wezterm": "",
    "org.wezfurlong.wezterm": "",
    "foot": "",
    "gnome-terminal": "",
    "nautilus": "󰉋",
    "org.gnome.Nautilus": "󰉋",
    "thunar": "󰉋",
    "dolphin": "󰉋",
    "code": "󰨞",
    "visual-studio-code": "󰨞",
    "vscodium": "󰨞",
    "gedit": "󰷈",
    "telegramdesktop": "",
    "org.telegram.desktop": "",
    "discord": "",
    "spotify": "",
    "spotify-launcher": "",
    "obsidian": "󱓧",
    "steam": "󰓓",
    "gimp": "",
    "inkscape": "",
    "blender": "󰂫",
    "mpv": "",
    "vlc": "󰕼",
    "hiddify": "󰒄",
    "anki": "󰠮",
    "default": "󰣆"
}

def get_config_file(filename):
    for d in CONFIG_DIRS:
        p = d / filename
        if p.exists():
            return p
    # Fallback to creating in ~/.config/niri-panel
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

def save_pinned(pinned_list):
    p = get_config_file("pinned.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(pinned_list, f, indent=2)

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

def get_dot_indicators(count):
    if count <= 0:
        return ""
    if count == 1:
        return " ●"
    if count == 2:
        return " ●●"
    if count == 3:
        return " ●●●"
    return f" ●{count}"

def build_taskbar_state():
    pinned_apps = load_pinned()
    running_windows = get_niri_windows()
    
    # Group running windows by app_id
    grouped_windows = {}
    for win in running_windows:
        app_id = win.get("app_id") or win.get("appId") or "unknown"
        if app_id not in grouped_windows:
            grouped_windows[app_id] = []
        grouped_windows[app_id].append(win)
        
    apps = []
    seen_app_ids = set()

    # 1. Process Pinned Apps
    for pin in pinned_apps:
        app_id = pin.get("app_id", "")
        seen_app_ids.add(app_id)
        
        # Check if running
        windows = grouped_windows.get(app_id, [])
        # Also check for alternate case / sub-matches
        if not windows:
            for k, wins in grouped_windows.items():
                if k.lower() == app_id.lower() or app_id.lower() in k.lower():
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

    # 2. Process Unpinned Running Apps
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

def format_waybar_taskbar():
    apps = build_taskbar_state()
    items = []
    tooltip_lines = ["<b>Applications:</b>"]
    
    classes = ["taskbar-container"]
    if any(a["is_active"] for a in apps):
        classes.append("has-active")

    for a in apps:
        glyph = a["glyph"]
        dots = get_dot_indicators(a["window_count"]) if a["is_running"] else ""
        item_text = f"{glyph}{dots}"
        items.append(item_text)
        
        status = "● Active" if a["is_active"] else ("Running" if a["is_running"] else "Pinned")
        cnt = f" ({a['window_count']} windows)" if a["window_count"] > 1 else ""
        tooltip_lines.append(f"• <b>{a['name']}</b>{cnt} - <i>{status}</i>")

    text_repr = "   ".join(items) if items else "󰣆"
    tooltip = "\n".join(tooltip_lines)
    
    return json.dumps({
        "text": text_repr,
        "alt": "taskbar",
        "tooltip": tooltip,
        "class": classes
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
        # Default to first active or first running
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

    # Scenario 3: Multiple Windows -> Open Window Grouping Selector Popup
    script_dir = Path(__file__).resolve().parent
    window_menu_py = script_dir.parent / "popup" / "taskbar" / "window_menu.py"
    if window_menu_py.exists():
        subprocess.Popen([sys.executable, str(window_menu_py), "--app", target_app["app_id"]])
    else:
        # Fallback focus first
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

def handle_pin_toggle(app_id, name=None, exec_cmd=None):
    pinned = load_pinned()
    existing = [p for p in pinned if p.get("app_id") == app_id]
    if existing:
        pinned = [p for p in pinned if p.get("app_id") != app_id]
    else:
        pinned.append({
            "name": name or app_id.capitalize(),
            "app_id": app_id,
            "icon": app_id,
            "exec": exec_cmd or app_id,
            "autostart": False
        })
    save_pinned(pinned)

def stream_taskbar():
    prev_output = ""
    while True:
        curr_output = format_waybar_taskbar()
        if curr_output != prev_output:
            print(curr_output, flush=True)
            prev_output = curr_output
        time.sleep(0.5)

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
        elif cmd == "--pin-toggle":
            app_id = sys.argv[2] if len(sys.argv) > 2 else ""
            name = sys.argv[3] if len(sys.argv) > 3 else None
            exec_cmd = sys.argv[4] if len(sys.argv) > 4 else None
            handle_pin_toggle(app_id, name, exec_cmd)
        elif cmd == "--json":
            print(json.dumps(build_taskbar_state(), indent=2))
        else:
            print(format_waybar_taskbar())
    else:
        print(format_waybar_taskbar())
