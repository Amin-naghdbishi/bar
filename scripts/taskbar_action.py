#!/usr/bin/env python3
"""
CLI bridge for Waybar taskbar clicks and events
"""
import sys
import subprocess
from pathlib import Path

def main():
    script_dir = Path(__file__).resolve().parent
    taskbar_py = script_dir / "taskbar.py"
    
    args = sys.argv[1:]
    subprocess.run([sys.executable, str(taskbar_py)] + args)

if __name__ == "__main__":
    main()
