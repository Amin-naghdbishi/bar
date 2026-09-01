#!/usr/bin/env bash
# =============================================================================
# Professional Niri Waybar Panel - Installation Script
# Supports: Arch Linux (pacman/yay/paru), Debian/Ubuntu, Fedora
# =============================================================================

set -e

COLOR_RESET="\033[0m"
COLOR_BOLD="\033[1m"
COLOR_GREEN="\033[1;32m"
COLOR_BLUE="\033[1;34m"
COLOR_YELLOW="\033[1;33m"
COLOR_RED="\033[1;31m"
COLOR_CYAN="\033[1;36m"

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_PANEL_DIR="$HOME/.config/niri-panel"
TARGET_WAYBAR_DIR="$HOME/.config/waybar"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

echo -e "${COLOR_BLUE}${COLOR_BOLD}"
echo "================================================================="
echo "       Professional Niri Waybar Desktop Panel Installer"
echo "================================================================="
echo -e "${COLOR_RESET}"

# -----------------------------------------------------------------------------
# 1. Dependency Check & Installation
# -----------------------------------------------------------------------------
echo -e "${COLOR_CYAN}[1/6] Checking system dependencies...${COLOR_RESET}"

ARCH_DEPS=(
    "waybar"
    "python"
    "python-gobject"
    "gtk3"
    "gtk-layer-shell"
    "pipewire"
    "wireplumber"
    "bluez-utils"
    "upower"
    "brightnessctl"
    "wlsunset"
    "ttf-nerd-fonts-symbols"
    "papirus-icon-theme"
)

DEBIAN_DEPS=(
    "waybar"
    "python3"
    "python3-gi"
    "python3-gi-cairo"
    "gir1.2-gtk-3.0"
    "gir1.2-gtk-layer-shell-0.1"
    "pipewire"
    "wireplumber"
    "bluez"
    "upower"
    "brightnessctl"
    "wlsunset"
    "fonts-font-awesome"
    "papirus-icon-theme"
)

FEDORA_DEPS=(
    "waybar"
    "python3"
    "python3-gobject"
    "gtk3"
    "gtk-layer-shell"
    "pipewire"
    "wireplumber"
    "bluez"
    "upower"
    "brightnessctl"
    "wlsunset"
    "fontawesome-fonts"
    "papirus-icon-theme"
)

install_dependencies() {
    if command -v pacman >/dev/null 2>&1; then
        echo -e "${COLOR_YELLOW}Arch Linux detected. Installing missing packages via pacman...${COLOR_RESET}"
        if command -v sudo >/dev/null 2>&1; then
            sudo pacman -S --needed --noconfirm "${ARCH_DEPS[@]}" || true
        else
            pacman -S --needed --noconfirm "${ARCH_DEPS[@]}" || true
        fi
    elif command -v apt-get >/dev/null 2>&1; then
        echo -e "${COLOR_YELLOW}Debian/Ubuntu detected. Installing missing packages via apt...${COLOR_RESET}"
        if command -v sudo >/dev/null 2>&1; then
            sudo apt-get update && sudo apt-get install -y "${DEBIAN_DEPS[@]}" || true
        fi
    elif command -v dnf >/dev/null 2>&1; then
        echo -e "${COLOR_YELLOW}Fedora detected. Installing missing packages via dnf...${COLOR_RESET}"
        if command -v sudo >/dev/null 2>&1; then
            sudo dnf install -y "${FEDORA_DEPS[@]}" || true
        fi
    else
        echo -e "${COLOR_YELLOW}Note: Unknown package manager. Please ensure waybar, python3-gobject, gtk3, gtk-layer-shell, and pipewire are installed.${COLOR_RESET}"
    fi
}

if [ "$1" == "--install-deps" ] || [ "$1" == "-y" ]; then
    install_dependencies
else
    echo -e "Required packages: ${COLOR_BOLD}waybar, python-gobject, gtk3, gtk-layer-shell, wireplumber, upower, brightnessctl${COLOR_RESET}"
fi

# -----------------------------------------------------------------------------
# 2. Backup Existing Configurations
# -----------------------------------------------------------------------------
echo -e "${COLOR_CYAN}[2/6] Backing up existing configurations...${COLOR_RESET}"

if [ -d "$TARGET_WAYBAR_DIR" ]; then
    BACKUP_WAYBAR="${TARGET_WAYBAR_DIR}.backup-${TIMESTAMP}"
    echo -e "  Backing up ${COLOR_BOLD}${TARGET_WAYBAR_DIR}${COLOR_RESET} to ${COLOR_BOLD}${BACKUP_WAYBAR}${COLOR_RESET}"
    cp -r "$TARGET_WAYBAR_DIR" "$BACKUP_WAYBAR"
fi

if [ -d "$TARGET_PANEL_DIR" ]; then
    BACKUP_PANEL="${TARGET_PANEL_DIR}.backup-${TIMESTAMP}"
    echo -e "  Backing up ${COLOR_BOLD}${TARGET_PANEL_DIR}${COLOR_RESET} to ${COLOR_BOLD}${BACKUP_PANEL}${COLOR_RESET}"
    cp -r "$TARGET_PANEL_DIR" "$BACKUP_PANEL"
fi

# -----------------------------------------------------------------------------
# 3. Create Target Directories
# -----------------------------------------------------------------------------
echo -e "${COLOR_CYAN}[3/6] Setting up directories...${COLOR_RESET}"
mkdir -p "$TARGET_WAYBAR_DIR"
mkdir -p "$TARGET_PANEL_DIR"
mkdir -p "$TARGET_PANEL_DIR/scripts"
mkdir -p "$TARGET_PANEL_DIR/popup"
mkdir -p "$TARGET_PANEL_DIR/config"
mkdir -p "$TARGET_PANEL_DIR/assets"

# -----------------------------------------------------------------------------
# 4. Copy Panel Files
# -----------------------------------------------------------------------------
echo -e "${COLOR_CYAN}[4/6] Installing panel components...${COLOR_RESET}"

# Copy Waybar config and style
cp "$SOURCE_DIR/waybar/config.jsonc" "$TARGET_WAYBAR_DIR/config.jsonc"
cp "$SOURCE_DIR/waybar/style.css" "$TARGET_WAYBAR_DIR/style.css"

# Copy Scripts
cp -r "$SOURCE_DIR/scripts/"* "$TARGET_PANEL_DIR/scripts/"
chmod +x "$TARGET_PANEL_DIR/scripts/"*.py "$TARGET_PANEL_DIR/scripts/"*.sh 2>/dev/null || true

# Copy Popups
cp -r "$SOURCE_DIR/popup/"* "$TARGET_PANEL_DIR/popup/"
find "$TARGET_PANEL_DIR/popup" -type f -name "*.py" -exec chmod +x {} +

# Copy Config and Assets
cp -r "$SOURCE_DIR/config/"* "$TARGET_PANEL_DIR/config/"
cp -r "$SOURCE_DIR/assets/"* "$TARGET_PANEL_DIR/assets/"

# -----------------------------------------------------------------------------
# 5. Verify Permissions & Executables
# -----------------------------------------------------------------------------
echo -e "${COLOR_CYAN}[5/6] Verifying permissions and paths...${COLOR_RESET}"
chmod +x "$SOURCE_DIR/install.sh" "$SOURCE_DIR/uninstall.sh" 2>/dev/null || true

# -----------------------------------------------------------------------------
# 6. Restart Waybar (if running)
# -----------------------------------------------------------------------------
echo -e "${COLOR_CYAN}[6/6] Reloading desktop panel...${COLOR_RESET}"
if pgrep -x "waybar" >/dev/null 2>&1; then
    echo "  Restarting Waybar daemon..."
    killall waybar 2>/dev/null || true
    sleep 0.3
    if command -v waybar >/dev/null 2>&1; then
        waybar &
    fi
fi

echo ""
echo -e "${COLOR_GREEN}${COLOR_BOLD}================================================================="
echo "   Professional Niri Waybar Panel Installed Successfully!"
echo "=================================================================${COLOR_RESET}"
echo ""
echo -e "Panel Configuration:  ${COLOR_BOLD}${TARGET_WAYBAR_DIR}/config.jsonc${COLOR_RESET}"
echo -e "Panel Stylesheet:     ${COLOR_BOLD}${TARGET_WAYBAR_DIR}/style.css${COLOR_RESET}"
echo -e "Scripts & Popups:     ${COLOR_BOLD}${TARGET_PANEL_DIR}/${COLOR_RESET}"
echo -e "Pinned Applications:  ${COLOR_BOLD}${TARGET_PANEL_DIR}/config/pinned.json${COLOR_RESET}"
echo ""
echo -e "${COLOR_CYAN}Niri Autostart Tip:${COLOR_RESET}"
echo "Add the following line to your ~/.config/niri/config.kdl to run Waybar on startup:"
echo -e "${COLOR_BOLD}    spawn-at-startup \"waybar\"${COLOR_RESET}"
echo ""
echo -e "To uninstall, simply run: ${COLOR_BOLD}./uninstall.sh${COLOR_RESET}"
echo ""
