"""
Audio backend using PipeWire / WirePlumber (wpctl) & PulseAudio (pactl)
"""

import json
import re
import subprocess

class AudioBackend:
    @staticmethod
    def get_master_volume():
        vol = 70
        is_muted = False
        try:
            p = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0:
                m = re.search(r"Volume:\s*([\d\.]+)", p.stdout)
                if m:
                    vol = int(float(m.group(1)) * 100)
                if "[MUTED]" in p.stdout:
                    is_muted = True
        except Exception:
            try:
                p = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], capture_output=True, text=True, timeout=1)
                m = re.search(r"(\d+)%", p.stdout)
                if m:
                    vol = int(m.group(1))
                pm = subprocess.run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], capture_output=True, text=True, timeout=1)
                if "yes" in pm.stdout.lower():
                    is_muted = True
            except Exception:
                pass
        return vol, is_muted

    @staticmethod
    def set_master_volume(vol_pct):
        vol_float = max(0, min(150, vol_pct)) / 100.0
        try:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{vol_float:.2f}"])
        except Exception:
            try:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{int(vol_pct)}%"])
            except Exception:
                pass

    @staticmethod
    def toggle_master_mute():
        try:
            subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
        except Exception:
            try:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
            except Exception:
                pass

    @staticmethod
    def get_mic_volume():
        vol = 60
        is_muted = False
        try:
            p = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0:
                m = re.search(r"Volume:\s*([\d\.]+)", p.stdout)
                if m:
                    vol = int(float(m.group(1)) * 100)
                if "[MUTED]" in p.stdout:
                    is_muted = True
        except Exception:
            try:
                p = subprocess.run(["pactl", "get-source-volume", "@DEFAULT_SOURCE@"], capture_output=True, text=True, timeout=1)
                m = re.search(r"(\d+)%", p.stdout)
                if m:
                    vol = int(m.group(1))
                pm = subprocess.run(["pactl", "get-source-mute", "@DEFAULT_SOURCE@"], capture_output=True, text=True, timeout=1)
                if "yes" in pm.stdout.lower():
                    is_muted = True
            except Exception:
                pass
        return vol, is_muted

    @staticmethod
    def set_mic_volume(vol_pct):
        vol_float = max(0, min(100, vol_pct)) / 100.0
        try:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SOURCE@", f"{vol_float:.2f}"])
        except Exception:
            try:
                subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{int(vol_pct)}%"])
            except Exception:
                pass

    @staticmethod
    def toggle_mic_mute():
        try:
            subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"])
        except Exception:
            try:
                subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"])
            except Exception:
                pass

    @staticmethod
    def get_sinks():
        sinks = []
        # Try pactl json first
        try:
            p = subprocess.run(["pactl", "-f", "json", "list", "sinks"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0:
                data = json.loads(p.stdout)
                for item in data:
                    sinks.append({
                        "id": str(item.get("index", "")),
                        "name": item.get("name", ""),
                        "description": item.get("description", item.get("name", "Unknown Sink")),
                        "is_default": item.get("state") == "RUNNING" or "default" in item.get("name", "").lower()
                    })
        except Exception:
            pass

        if not sinks:
            # Fallback default sinks
            sinks = [
                {"id": "1", "name": "speakers", "description": "Built-in Speakers / Headphones", "is_default": True},
                {"id": "2", "name": "hdmi", "description": "HDMI / DisplayPort Audio", "is_default": False}
            ]
        return sinks

    @staticmethod
    def set_default_sink(sink_id_or_name):
        try:
            subprocess.run(["wpctl", "set-default", str(sink_id_or_name)])
        except Exception:
            try:
                subprocess.run(["pactl", "set-default-sink", str(sink_id_or_name)])
            except Exception:
                pass

    @staticmethod
    def get_app_streams():
        streams = []
        try:
            p = subprocess.run(["pactl", "-f", "json", "list", "sink-inputs"], capture_output=True, text=True, timeout=1)
            if p.returncode == 0:
                data = json.loads(p.stdout)
                for item in data:
                    props = item.get("properties", {})
                    app_name = props.get("application.name", props.get("media.name", "Audio Stream"))
                    vol_pct = 100
                    vol_dict = item.get("volume", {})
                    if vol_dict:
                        # e.g. {"front-left": {"value_percent": "80%"}}
                        for ch, ch_data in vol_dict.items():
                            if isinstance(ch_data, dict) and "value_percent" in ch_data:
                                m = re.search(r"(\d+)%", str(ch_data["value_percent"]))
                                if m:
                                    vol_pct = int(m.group(1))
                                    break
                    streams.append({
                        "id": str(item.get("index")),
                        "name": app_name,
                        "volume": vol_pct,
                        "muted": item.get("mute", False)
                    })
        except Exception:
            pass

        return streams

    @staticmethod
    def set_app_volume(stream_id, vol_pct):
        try:
            subprocess.run(["pactl", "set-sink-input-volume", str(stream_id), f"{int(vol_pct)}%"])
        except Exception:
            pass

    @staticmethod
    def toggle_app_mute(stream_id):
        try:
            subprocess.run(["pactl", "set-sink-input-mute", str(stream_id), "toggle"])
        except Exception:
            pass
