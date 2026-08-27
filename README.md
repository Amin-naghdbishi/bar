# Minimal Windows 11-Style Waybar for Niri

A minimal, modern, dark frosted-glass taskbar for [Niri](https://github.com/YaLTeR/niri) built using native [Waybar](https://github.com/Alexays/Waybar) modules.

---

## 🖥️ Layout Overview

```text
[ 1 ] Active Window Title                  [App Icons] [] [20:42] [EN] [124G] [] [6.2G] [ 87%] [] []
└─────── Left Side ───────┘                  └─────────────── Right Side ────────────────────────────────┘
```

* **Position**: Bottom edge-to-edge full width
* **Height**: 32px (thin and compact)
* **Visual Style**: Dark semi-transparent frosted glass with a subtle 1px top border
* **Typography**: Primary font set to **Asam**, with seamless icon fallbacks (Font Awesome & Nerd Font)

---

## 📋 Module Details & Ordering

### 1. Left Side
* **Current Workspace (`niri/workspaces`)**:
  * Displays **only** the currently active workspace number (`1`, `2`, `5`).
  * Inactive workspaces are omitted (`"current-only": true`).
  * Automatically reacts and updates when switching workspaces.
* **Active Window (`niri/window`)**:
  * Shows the focused application/window title in plain text.
  * No application icon in this section.
  * Dynamically updates on focus change.

### 2. Right Side: Applications
* **Taskbar (`wlr/taskbar`)**:
  * Clean, small 16px application icons for running windows.
  * Subtle Windows 11-style active window indicator (semi-transparent background highlight and bottom accent bar).
  * Click to focus/raise, middle-click to close.

### 3. Right Side: System Information
Placed strictly in the requested sequence:
1. **Wi-Fi (`network`)**: Simple Wi-Fi/network status icon (``).
2. **Clock (`clock`)**: Compact time display formatted as `{:%H:%M}` (e.g. `20:42`).
3. **Keyboard Layout (`niri/language`)**: Short uppercase layout indicator (e.g. `EN`, `DE`).
4. **Free Disk Space (`disk`)**: Compact available space formatted as `{specific_free:0.0f}G` (e.g. `124G`).
5. **Home (`custom/home`)**: Clean house icon (``) that opens the home directory on click.
6. **RAM (`memory`)**: Used RAM in compact format formatted as `{used:0.1f}G` (e.g. `6.2G`).
7. **Battery (`battery`)**: Dynamic battery icon and capacity percentage (e.g. `87%`).
8. **Volume (`pulseaudio`)**: Compact speaker icon (`` / `` / `` / `` when muted). Click toggles mute; right click opens `pavucontrol`.
9. **Microphone (`pulseaudio#microphone`)**: Microphone icon (`` / `` when muted). Click toggles mute.

---

## 🚀 How to Launch & Reload Waybar

### Option A: Launch from `~/bar`
```bash
waybar -c ~/bar/config.jsonc -s ~/bar/style.css &
```

### Option B: Launch from standard config path
```bash
waybar &
```

### Reloading Waybar (without killing existing windows)
```bash
killall -SIGUSR2 waybar
# or
pkill -SIGUSR2 waybar
```

### Restarting Waybar
```bash
killall waybar 2>/dev/null; waybar &
```

### Automatically Launch with Niri
In your Niri configuration (`~/.config/niri/config.kdl`):
```kdl
spawn-at-startup "waybar"
```
Or with custom paths:
```kdl
spawn-at-startup "waybar" "-c" "~/.config/waybar/config.jsonc" "-s" "~/.config/waybar/style.css"
```
