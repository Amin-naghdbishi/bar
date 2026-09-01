"""
Bluetooth backend using BlueZ / bluetoothctl
"""

import subprocess
import re

class BluetoothBackend:
    @staticmethod
    def is_powered():
        try:
            p = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True, timeout=1)
            return "Powered: yes" in p.stdout
        except Exception:
            return False

    @staticmethod
    def set_power(power_on):
        cmd = "on" if power_on else "off"
        try:
            subprocess.run(["bluetoothctl", "power", cmd], timeout=2)
        except Exception:
            pass

    @staticmethod
    def get_connected_devices():
        devices = []
        try:
            p = subprocess.run(["bluetoothctl", "devices", "Connected"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0:
                for line in p.stdout.splitlines():
                    # Format: Device XX:XX:XX:XX:XX:XX Name
                    parts = line.strip().split(" ", 2)
                    if len(parts) >= 3 and parts[0] == "Device":
                        mac = parts[1]
                        name = parts[2]
                        
                        # Get device info for icon and battery
                        icon = "󰂱"
                        battery = ""
                        try:
                            p_info = subprocess.run(["bluetoothctl", "info", mac], capture_output=True, text=True, timeout=1)
                            if "Icon: audio-headset" in p_info.stdout or "head" in name.lower() or "buds" in name.lower():
                                icon = "󰋋"
                            elif "Icon: input-mouse" in p_info.stdout or "mouse" in name.lower():
                                icon = "󰍽"
                            elif "Icon: input-keyboard" in p_info.stdout or "keyboard" in name.lower():
                                icon = "󰌌"
                            elif "Icon: phone" in p_info.stdout or "phone" in name.lower():
                                icon = "󰏲"
                            
                            m_bat = re.search(r"Battery Percentage:\s*(0x[0-9a-fA-F]+|\d+)", p_info.stdout)
                            if m_bat:
                                val = m_bat.group(1)
                                if val.startswith("0x"):
                                    battery = f"{int(val, 16)}%"
                                else:
                                    battery = f"{val}%"
                        except Exception:
                            pass

                        devices.append({
                            "mac": mac,
                            "name": name,
                            "icon": icon,
                            "battery": battery,
                            "connected": True
                        })
        except Exception:
            pass
        return devices

    @staticmethod
    def get_paired_and_available_devices():
        devices = []
        try:
            p = subprocess.run(["bluetoothctl", "devices", "Paired"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0:
                for line in p.stdout.splitlines():
                    parts = line.strip().split(" ", 2)
                    if len(parts) >= 3 and parts[0] == "Device":
                        mac = parts[1]
                        name = parts[2]
                        
                        icon = "󰂯"
                        if "head" in name.lower() or "buds" in name.lower():
                            icon = "󰋋"
                        elif "mouse" in name.lower():
                            icon = "󰍽"
                        elif "keyboard" in name.lower():
                            icon = "󰌌"

                        devices.append({
                            "mac": mac,
                            "name": name,
                            "icon": icon,
                            "connected": False
                        })
        except Exception:
            pass
        return devices

    @staticmethod
    def connect_device(mac):
        try:
            subprocess.Popen(["bluetoothctl", "connect", mac])
        except Exception:
            pass

    @staticmethod
    def disconnect_device(mac):
        try:
            subprocess.run(["bluetoothctl", "disconnect", mac], timeout=2)
        except Exception:
            pass

    @staticmethod
    def pair_device(mac):
        try:
            subprocess.Popen(["bluetoothctl", "pair", mac])
        except Exception:
            pass

    @staticmethod
    def start_scan():
        try:
            subprocess.Popen(["bluetoothctl", "--timeout", "10", "scan", "on"])
        except Exception:
            pass
