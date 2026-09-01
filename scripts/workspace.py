#!/usr/bin/env python3
"""
Niri Workspace Indicator for Waybar
Streams current active workspace number as clean JSON.
Requirements:
- Only shows the current workspace number (e.g. 1, 2, 3)
- No buttons, no workspace list, no switcher
- Smooth change indication
"""

import json
import os
import subprocess
import sys
import time

def get_niri_workspaces():
    try:
        proc = subprocess.run(
            ["niri", "msg", "-j", "workspaces"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout)
    except Exception:
        pass
    return None

def get_active_workspace():
    workspaces = get_niri_workspaces()
    if workspaces:
        # Check if list of workspace objects
        if isinstance(workspaces, list):
            for ws in workspaces:
                if ws.get("is_active") or ws.get("is_focused"):
                    # Use idx if available (1-indexed), else name or id
                    idx = ws.get("idx")
                    if idx is not None:
                        return str(idx)
                    return str(ws.get("name", ws.get("id", "1")))
            if len(workspaces) > 0:
                first = workspaces[0]
                return str(first.get("idx", first.get("name", first.get("id", "1"))))
        elif isinstance(workspaces, dict):
            # Dict of workspaces
            for k, ws in workspaces.items():
                if isinstance(ws, dict) and (ws.get("is_active") or ws.get("is_focused")):
                    return str(ws.get("idx", ws.get("name", k)))
    return "1"

def format_output(ws_num, prev_num=None):
    text = str(ws_num)
    tooltip = f"Workspace {ws_num}\n(Niri Compositor)\nSwitch with Mod+1..9 or Mod+Wheel"
    classes = ["workspace-indicator", f"workspace-{ws_num}"]
    
    # If transitioning, add transition class
    if prev_num is not None and prev_num != ws_num:
        classes.append("workspace-transition")
        
    return json.dumps({
        "text": text,
        "alt": f"workspace-{ws_num}",
        "tooltip": tooltip,
        "class": classes
    })

def stream_events():
    prev_ws = None
    curr_ws = get_active_workspace()
    print(format_output(curr_ws), flush=True)
    prev_ws = curr_ws

    # Try streaming from niri msg event-stream
    try:
        p = subprocess.Popen(
            ["niri", "msg", "event-stream"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )
        for line in p.stdout:
            if not line:
                break
            # Whenever an event happens, check active workspace
            new_ws = get_active_workspace()
            if new_ws != curr_ws:
                prev_ws = curr_ws
                curr_ws = new_ws
                print(format_output(curr_ws, prev_ws), flush=True)
    except Exception:
        # Fallback to periodic polling
        while True:
            time.sleep(0.5)
            new_ws = get_active_workspace()
            if new_ws != curr_ws:
                prev_ws = curr_ws
                curr_ws = new_ws
                print(format_output(curr_ws, prev_ws), flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        stream_events()
    else:
        print(format_output(get_active_workspace()))
