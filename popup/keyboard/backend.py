"""
Keyboard layout backend for Niri compositor
"""

import json
import subprocess

class KeyboardBackend:
    @staticmethod
    def get_layouts():
        layouts = []
        cur_idx = 0

        # Query Niri IPC
        try:
            p = subprocess.run(["niri", "msg", "-j", "keyboard-layouts"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0 and p.stdout.strip():
                data = json.loads(p.stdout)
                names = data.get("names", [])
                cur_idx = data.get("current_idx", 0)
                for idx, name in enumerate(names):
                    code = "EN"
                    nl = name.lower()
                    if "persian" in nl or "farsi" in nl or "fa" in nl:
                        code = "FA"
                    elif "german" in nl or "de" in nl:
                        code = "DE"
                    elif "french" in nl or "fr" in nl:
                        code = "FR"
                    elif "spanish" in nl or "es" in nl:
                        code = "ES"
                    elif "arabic" in nl or "ar" in nl:
                        code = "AR"
                    elif "russian" in nl or "ru" in nl:
                        code = "RU"
                    
                    layouts.append({
                        "idx": idx,
                        "name": name,
                        "code": code,
                        "is_active": (idx == cur_idx)
                    })
        except Exception:
            pass

        if not layouts:
            # Fallback default list
            layouts = [
                {"idx": 0, "name": "English (US)", "code": "EN", "is_active": True},
                {"idx": 1, "name": "Persian (Farsi)", "code": "FA", "is_active": False}
            ]
        return layouts, cur_idx

    @staticmethod
    def switch_to_layout(idx):
        try:
            subprocess.run(["niri", "msg", "action", "switch-layout", str(idx)])
        except Exception:
            pass
