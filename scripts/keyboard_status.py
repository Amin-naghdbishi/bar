#!/usr/bin/env python3
"""
Clean Keyboard Layout Indicator for Waybar
- Shows 2-letter uppercase layout code (EN, FA, etc.)
- No tooltips (clicking opens the real Keyboard Layout Center popup window)
"""

import json
import subprocess
import sys

def get_layout_code():
    code = "EN"
    try:
        proc = subprocess.run(["niri", "msg", "-j", "keyboard-layouts"], capture_output=True, text=True, timeout=1)
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            names = data.get("names", [])
            idx = data.get("current_idx", 0)
            if names and 0 <= idx < len(names):
                fn_lower = names[idx].lower()
                if "persian" in fn_lower or "farsi" in fn_lower or "fa" in fn_lower:
                    code = "FA"
                elif "german" in fn_lower or "de" in fn_lower:
                    code = "DE"
                elif "french" in fn_lower or "fr" in fn_lower:
                    code = "FR"
                elif "spanish" in fn_lower or "es" in fn_lower:
                    code = "ES"
                elif "arabic" in fn_lower or "ar" in fn_lower:
                    code = "AR"
                elif "russian" in fn_lower or "ru" in fn_lower:
                    code = "RU"
                else:
                    code = "EN"
    except Exception:
        pass
    return code

def main():
    code = get_layout_code()
    print(json.dumps({
        "text": code,
        "alt": f"keyboard-{code.lower()}",
        "tooltip": False,
        "class": ["keyboard-module", f"layout-{code.lower()}"]
    }))

if __name__ == "__main__":
    main()
