#!/usr/bin/env bash
# =============================================================================
# Professional Niri Waybar Panel - Uninstallation Script
# Restores previous backup and cleans installed panel files
# =============================================================================

set -e

COLOR_RESET="\033[0m"
COLOR_BOLD="\033[1m"
COLOR_GREEN="\033[1;32m"
COLOR_BLUE="\033[1;34m"
COLOR_YELLOW="\033[1;33m"
COLOR_RED="\033[1;31m"
COLOR_CYAN="\033[1;36m"

TARGET_PANEL_DIR="$HOME/.config/niri-panel"
TARGET_WAYBAR_DIR="$HOME/.config/waybar"

echo -e "${COLOR_YELLOW}${COLOR_BOLD}"
echo "================================================================="
echo "       Professional Niri Waybar Desktop Panel Uninstaller"
echo "================================================================="
echo -e "${COLOR_RESET}"

read -p "Are you sure you want to uninstall the Niri Waybar panel? [y/N]: " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

# 1. Terminate running popups and helper processes
echo -e "${COLOR_CYAN}[1/4] Stopping panel daemons and active popups...${COLOR_RESET}"
pkill -f "popup_manager.py" 2>/dev/null || true
pkill -f "niri-panel" 2>/dev/null || true
rm -rf /tmp/niri-panel-popups 2>/dev/null || true

# 2. Remove panel files
echo -e "${COLOR_CYAN}[2/4] Removing panel directory (~/.config/niri-panel)...${COLOR_RESET}"
if [ -d "$TARGET_PANEL_DIR" ]; then
    rm -rf "$TARGET_PANEL_DIR"
fi

# 3. Restore backup if available
echo -e "${COLOR_CYAN}[3/4] Checking for configuration backups...${COLOR_RESET}"
LATEST_BACKUP=$(ls -d "$HOME"/.config/waybar.backup-* 2>/dev/null | sort -r | head -n 1 || true)

if [ -n "$LATEST_BACKUP" ] && [ -d "$LATEST_BACKUP" ]; then
    echo -e "${COLOR_GREEN}  Found backup: ${LATEST_BACKUP}${COLOR_RESET}"
    rm -rf "$TARGET_WAYBAR_DIR"
    cp -r "$LATEST_BACKUP" "$TARGET_WAYBAR_DIR"
    echo "  Restored original Waybar configuration."
else
    echo "  No previous Waybar backup found. Removing Waybar config files installed by this project."
    rm -f "$TARGET_WAYBAR_DIR/config.jsonc" "$TARGET_WAYBAR_DIR/style.css"
fi

# 4. Restart Waybar if appropriate
echo -e "${COLOR_CYAN}[4/4] Finalizing system state...${COLOR_RESET}"
if pgrep -x "waybar" >/dev/null 2>&1; then
    killall waybar 2>/dev/null || true
    sleep 0.3
    if [ -f "$TARGET_WAYBAR_DIR/config" ] || [ -f "$TARGET_WAYBAR_DIR/config.jsonc" ]; then
        waybar &
    fi
fi

echo ""
echo -e "${COLOR_GREEN}${COLOR_BOLD}================================================================="
echo "   Niri Waybar Panel Uninstalled and Cleaned Successfully!"
echo "=================================================================${COLOR_RESET}"
echo ""
