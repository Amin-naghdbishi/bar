#!/usr/bin/env python3
"""
Individual Application Taskbar Button Slot for Waybar
- Renders an independent button for each application
- Resolves Papirus application icons with instant caching
- Displays centered window indicator dots directly underneath the icon
- Limits dots to 5 and appends number for 6+ windows (● ● ● ● ● 6)
- Handles click (launch/focus/group selector) and right-click (context menu)
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.icon_resolver import resolve_app_icon, resolve_app_icon_path, resolve_app_icon_name

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

def get_apps_list():
    pinned_apps = load_pinned()
    running_windows = get_niri_windows()
    
    # Group running windows by app_id
    grouped_windows = {}
    for win in running_windows:
        app_id = (win.get("app_id") or win.get("appId") or "unknown").lower()
        if app_id not in grouped_windows:
            grouped_windows[app_id] = []
        grouped_windows[app_id].append(win)
        
    apps = []
    seen_app_ids = set()

    # 1. Process Pinned Apps
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
            "icon": resolve_app_icon(app_id),
            "icon_path": str(resolve_app_icon_path(app_id) or ""),
            "icon_name": resolve_app_icon_name(app_id)
        })

    # 2. Process Running Unpinned Apps
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
            "icon": resolve_app_icon(app_id),
            "icon_path": str(resolve_app_icon_path(app_id) or ""),
            "icon_name": resolve_app_icon_name(app_id)
        })

    return apps

def format_dots_underneath(count, is_active):
    if count <= 0:
        return " "
    
    if count <= 5:
        dots = []
        for i in range(count):
            if is_active and i == 0:
                dots.append("<span color='#38bdf8'>•</span>")
            else:
                dots.append("<span color='#94a3b8'>•</span>")
        return " ".join(dots)
    else:
        dots = []
        for i in range(5):
            if is_active and i == 0:
                dots.append("<span color='#38bdf8'>•</span>")
            else:
                dots.append("<span color='#94a3b8'>•</span>")
        dots_str = " ".join(dots)
        return f"{dots_str} <span color='#cbd5e1' font='5'>{count}</span>"

def get_slot_output(slot_idx):
    apps = get_apps_list()
    if slot_idx < 0 or slot_idx >= len(apps):
        return json.dumps({
            "text": "",
            "alt": f"slot-{slot_idx}",
            "tooltip": False,
            "class": ["app-slot", "empty"]
        })

    app = apps[slot_idx]
    icon = app["icon"]
    dots_str = format_dots_underneath(app["window_count"], app["is_active"]) if app["is_running"] else " "

    if app["is_active"]:
        line1 = f"<span font='16' color='#ffffff'>{icon}</span>"
        line2 = f"<span font='5'>{dots_str}</span>"
        classes = ["app-slot", "active", f"app-{app['app_id']}"]
    elif app["is_running"]:
        line1 = f"<span font='16' color='#cbd5e1'>{icon}</span>"
        line2 = f"<span font='5'>{dots_str}</span>"
        classes = ["app-slot", "running", f"app-{app['app_id']}"]
    else:
        line1 = f"<span font='16' color='#64748b'>{icon}</span>"
        line2 = "<span font='5'> </span>"
        classes = ["app-slot", "pinned", f"app-{app['app_id']}"]

    text_content = f"{line1}\n{line2}"

    return json.dumps({
        "text": text_content,
        "alt": f"app-{app['app_id']}",
        "tooltip": False,
        "class": classes
    })

def handle_click(slot_idx):
    apps = get_apps_list()
    if slot_idx < 0 or slot_idx >= len(apps):
        return
    app = apps[slot_idx]

    if not app["is_running"]:
        subprocess.Popen(app["exec"], shell=True)
        return

    if app["window_count"] == 1:
        win_id = app["windows"][0].get("id")
        if win_id is not None:
            subprocess.run(["niri", "msg", "action", "focus-window", "--id", str(win_id)])
        return

    script_dir = Path(__file__).resolve().parent
    window_menu_py = script_dir.parent / "popup" / "taskbar" / "window_menu.py"
    if not window_menu_py.exists():
        window_menu_py = Path.home() / ".config" / "niri-panel" / "popup" / "taskbar" / "window_menu.py"
        
    if window_menu_py.exists():
        subprocess.Popen([sys.executable, str(window_menu_py), "--app", app["app_id"]])
    else:
        win_id = app["windows"][0].get("id")
        if win_id is not None:
            subprocess.run(["niri", "msg", "action", "focus-window", "--id", str(win_id)])

def handle_right_click(slot_idx):
    apps = get_apps_list()
    if slot_idx < 0 or slot_idx >= len(apps):
        return
    app = apps[slot_idx]

    script_dir = Path(__file__).resolve().parent
    context_menu_py = script_dir.parent / "popup" / "taskbar" / "context_menu.py"
    if not context_menu_py.exists():
        context_menu_py = Path.home() / ".config" / "niri-panel" / "popup" / "taskbar" / "context_menu.py"

    if context_menu_py.exists():
        subprocess.Popen([
            sys.executable,
            str(context_menu_py),
            "--app", app["app_id"],
            "--name", app["name"],
            "--exec", app["exec"],
            "--pinned", "1" if app["is_pinned"] else "0",
            "--running", "1" if app["is_running"] else "0"
        ])

def stream_slot(slot_idx):
    prev = ""
    while True:
        out = get_slot_output(slot_idx)
        if out != prev:
            print(out, flush=True)
            prev = out
        time.sleep(0.3)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "click" and len(sys.argv) > 2:
            handle_click(int(sys.argv[2]))
        elif cmd == "right-click" and len(sys.argv) > 2:
            handle_right_click(int(sys.argv[2]))
        elif cmd == "--watch" and len(sys.argv) > 2:
            stream_slot(int(sys.argv[2]))
        else:
            try:
                idx = int(cmd)
                print(get_slot_output(idx))
            except ValueError:
                print(get_slot_output(0))
    else:
        print(get_slot_output(0))
