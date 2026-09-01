"""
Battery and Power Management backend
Integrates with UPower, powerprofilesctl, brightnessctl, gammastep/wlsunset, sysfs
"""

import os
import re
import subprocess
from pathlib import Path

class BatteryBackend:
    @staticmethod
    def get_power_info():
        capacity = 100
        status = "Discharging"
        time_remaining = "3 hours remaining"
        is_ac = False
        has_battery = False
        health_pct = 98

        # 1. Sysfs inspection
        base = Path("/sys/class/power_supply")
        if base.exists():
            for bat in base.glob("BAT*"):
                has_battery = True
                try:
                    cap_f = bat / "capacity"
                    if cap_f.exists():
                        capacity = int(cap_f.read_text().strip())
                    stat_f = bat / "status"
                    if stat_f.exists():
                        status = stat_f.read_text().strip()
                except Exception:
                    pass
                break

            for ac in base.glob("AC*"):
                try:
                    online = (ac / "online").read_text().strip()
                    if online == "1":
                        is_ac = True
                except Exception:
                    pass

        # 2. UPower inspection
        try:
            p = subprocess.run(["upower", "-e"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0:
                for line in p.stdout.splitlines():
                    if "battery" in line:
                        has_battery = True
                        p_info = subprocess.run(["upower", "-i", line.strip()], capture_output=True, text=True, timeout=1)
                        for l in p_info.stdout.splitlines():
                            if "percentage:" in l:
                                m = re.search(r"(\d+)%", l)
                                if m:
                                    capacity = int(m.group(1))
                            elif "state:" in l:
                                status = l.split(":")[-1].strip().capitalize()
                            elif "time to empty:" in l:
                                time_remaining = l.split(":")[-1].strip() + " remaining"
                            elif "time to full:" in l:
                                time_remaining = l.split(":")[-1].strip() + " until full"
                            elif "capacity:" in l:
                                m = re.search(r"([\d\.]+)%", l)
                                if m:
                                    health_pct = float(m.group(1))
                        break
        except Exception:
            pass

        return {
            "capacity": capacity,
            "status": status,
            "is_ac": is_ac,
            "has_battery": has_battery,
            "time_remaining": time_remaining,
            "health": health_pct
        }

    @staticmethod
    def get_power_profile():
        try:
            p = subprocess.run(["powerprofilesctl", "get"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0 and p.stdout.strip():
                return p.stdout.strip()
        except Exception:
            pass
        return "balanced"

    @staticmethod
    def set_power_profile(profile_name):
        try:
            subprocess.run(["powerprofilesctl", "set", profile_name])
        except Exception:
            pass

    @staticmethod
    def get_brightness():
        try:
            p = subprocess.run(["brightnessctl", "g"], capture_output=True, text=True, timeout=1)
            p_max = subprocess.run(["brightnessctl", "m"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0 and p_max.returncode == 0:
                cur = int(p.stdout.strip())
                mx = int(p_max.stdout.strip())
                return int((cur / mx) * 100)
        except Exception:
            pass
        return 75

    @staticmethod
    def set_brightness(pct):
        pct = max(5, min(100, pct))
        try:
            subprocess.run(["brightnessctl", "s", f"{pct}%"])
        except Exception:
            pass

    @staticmethod
    def is_night_light_active():
        try:
            p = subprocess.run(["pgrep", "-f", "wlsunset|gammastep|hyprsunset"], capture_output=True, timeout=1)
            return p.returncode == 0
        except Exception:
            return False

    @staticmethod
    def toggle_night_light():
        if BatteryBackend.is_night_light_active():
            subprocess.run(["pkill", "-f", "wlsunset|gammastep|hyprsunset"])
        else:
            # Start night light daemon
            try:
                subprocess.Popen(["wlsunset", "-T", "4500", "-t", "3500"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                try:
                    subprocess.Popen(["gammastep", "-O", "4000K"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass

    @staticmethod
    def get_battery_limit_status():
        limit_paths = [
            "/sys/class/power_supply/BAT0/charge_control_limit_max",
            "/sys/class/power_supply/BAT1/charge_control_limit_max",
            "/sys/class/power_supply/BAT0/charge_stop_threshold"
        ]
        for p_str in limit_paths:
            p = Path(p_str)
            if p.exists():
                try:
                    val = int(p.read_text().strip())
                    return val <= 85
                except Exception:
                    pass
        return False

    @staticmethod
    def set_battery_limit(enable_80_limit):
        target_val = "80" if enable_80_limit else "100"
        limit_paths = [
            "/sys/class/power_supply/BAT0/charge_control_limit_max",
            "/sys/class/power_supply/BAT1/charge_control_limit_max",
            "/sys/class/power_supply/BAT0/charge_stop_threshold"
        ]
        for p_str in limit_paths:
            if os.path.exists(p_str):
                try:
                    subprocess.run(["pkexec", "sh", "-c", f"echo {target_val} > {p_str}"], timeout=2)
                except Exception:
                    pass

    @staticmethod
    def execute_power_action(action):
        if action == "lock":
            subprocess.Popen("swaylock -f -c 0b0f19 || hyprlock || gtklock || loginctl lock-session", shell=True)
        elif action == "suspend":
            subprocess.Popen(["systemctl", "suspend"])
        elif action == "reboot":
            subprocess.Popen(["systemctl", "reboot"])
        elif action == "poweroff":
            subprocess.Popen(["systemctl", "poweroff"])
