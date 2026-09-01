#!/usr/bin/env bash
# Autostart daemon for Niri Waybar panel
killall waybar 2>/dev/null || true
sleep 0.2
waybar &
