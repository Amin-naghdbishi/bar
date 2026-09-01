#!/usr/bin/env python3
"""
Clean Keyboard Layout Indicator for Waybar
Requirements:
- Shows 2-letter uppercase layout code (EN, FA, etc.)
- Detects active layout via Niri IPC or xkb
- Tooltip with full layout name
"""

import json
import subprocess
import sys

def get_layout_info():
    code = "EN"
    full_name = "English (US)"

    # Try Niri IPC
    try:
        proc = subprocess.run(
            ["niri", "msg", "-j", "keyboard-layouts"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            names = data.get("names", [])
            idx = data.get("current_idx", 0)
            if names and 0 <= idx < len(names):
                full_name = names[idx]
                # Infer 2 letter code
                fn_lower = full_name.lower()
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

    return code, full_name

def main():
    code, full_name = get_layout_info()
    
    tooltip = (
        f"<b>Keyboard Center</b>\n"
        f"• Active Layout: <b>{full_name}</b> ({code})\n\n"
        f"<i>Click to switch layout\n"
        f"Press Mod+Space in Niri to cycle</i>"
    )

    print(json.dumps({
        "text": code,
        "alt": f"keyboard-{code.lower()}",
        "tooltip": tooltip,
        "class": ["keyboard-module", f"layout-{code.lower()}"]
    }))

if __name__ == "__main__":
    main()
