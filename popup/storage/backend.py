"""
Storage backend
Analyzes mount points (/, /home) and user directories (Pictures, Videos, Music, Downloads, Documents)
"""

import os
import shutil
import subprocess
from pathlib import Path

class StorageBackend:
    @staticmethod
    def get_mount_usage(path_str):
        try:
            usage = shutil.disk_usage(path_str)
            tot_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            pct = (usage.used / usage.total)
            return {
                "path": path_str,
                "total_gb": tot_gb,
                "used_gb": used_gb,
                "free_gb": free_gb,
                "percentage": pct
            }
        except Exception:
            return {
                "path": path_str,
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "percentage": 0
            }

    @staticmethod
    def get_folder_size_gb(path):
        total_bytes = 0
        if not path.exists():
            return 0.0
        try:
            # Fast scan limited depth
            for root, dirs, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    if not os.path.islink(fp):
                        total_bytes += os.path.getsize(fp)
        except Exception:
            pass
        return total_bytes / (1024**3)

    @staticmethod
    def get_category_breakdown():
        home = Path.home()
        categories = [
            {"name": "Downloads", "path": home / "Downloads", "icon": "󰉍", "color": "#38bdf8"},
            {"name": "Videos", "path": home / "Videos", "icon": "󰉏", "color": "#a855f7"},
            {"name": "Pictures", "path": home / "Pictures", "icon": "󰉏", "color": "#ec4899"},
            {"name": "Documents", "path": home / "Documents", "icon": "󰉋", "color": "#3b82f6"},
            {"name": "Music", "path": home / "Music", "icon": "󰉐", "color": "#10b981"}
        ]

        # Calculate sizes
        for cat in categories:
            cat["size_gb"] = StorageBackend.get_folder_size_gb(cat["path"])

        # Sort largest first
        categories.sort(key=lambda x: x["size_gb"], reverse=True)

        # Compute max for relative scaling
        max_size = max([c["size_gb"] for c in categories] + [1.0])
        for cat in categories:
            cat["fraction"] = cat["size_gb"] / max_size

        return categories

    @staticmethod
    def open_folder(path_obj):
        try:
            subprocess.Popen(["xdg-open", str(path_obj)])
        except Exception:
            pass
