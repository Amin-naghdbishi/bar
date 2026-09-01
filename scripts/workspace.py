#!/usr/bin/env python3
"""
Niri Workspace Indicator for Waybar
- Only shows the active workspace number (e.g. 1, 2, 3)
- No tooltips
"""

import json
import subprocess
import sys
import time

def get_active_workspace():
    try:
        proc = subprocess.run(["niri", "msg", "-j", "workspaces"], capture_output=True, text=True, timeout=1)
        if proc.returncode == 0 and proc.stdout.strip():
            workspaces = json.loads(proc.stdout)
            if isinstance(workspaces, list):
                for ws in workspaces:
                    if ws.get("is_active") or ws.get("is_focused"):
                        idx = ws.get("idx")
                        if idx is not None:
                            return str(idx)
                        return str(ws.get("name", ws.get("id", "1")))
                if len(workspaces) > 0:
                    first = workspaces[0]
                    return str(first.get("idx", first.get("name", first.get("id", "1"))))
    except Exception:
        pass
    return "1"

def format_output(ws_num):
    return json.dumps({
        "text": str(ws_num),
        "alt": f"workspace-{ws_num}",
        "tooltip": False,
        "class": ["workspace-indicator", f"workspace-{ws_num}"]
    })

def stream_events():
    curr_ws = get_active_workspace()
    print(format_output(curr_ws), flush=True)

    try:
        p = subprocess.Popen(["niri", "msg", "event-stream"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        for line in p.stdout:
            if not line:
                break
            new_ws = get_active_workspace()
            if new_ws != curr_ws:
                curr_ws = new_ws
                print(format_output(curr_ws), flush=True)
    except Exception:
        while True:
            time.sleep(0.5)
            new_ws = get_active_workspace()
            if new_ws != curr_ws:
                curr_ws = new_ws
                print(format_output(curr_ws), flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        stream_events()
    else:
        print(format_output(get_active_workspace()))
