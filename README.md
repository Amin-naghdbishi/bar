# Linux Mint Cinnamon-Inspired Frosted Glass Waybar for Niri

A polished, desktop-oriented taskbar for [Niri](https://github.com/YaLTeR/niri) inspired by the **Linux Mint Cinnamon** panel usability, redesigned with a modern **transparent glass and soft blur effect**.

---

## 🖥️ Layout Overview

```text
[ 1 ]  [] [] [] ...                                    [ 100%] [ 75%] [ 6.2G] [ 124G] [ EN] [ 85%] [ 87%] [ 20:42]
└─ WS ─┴────── Open App Icons (Papirus) ──────┘           └──────────────────── Reversed System Tray ────────────────────┘
```

* **Position**: Bottom edge-to-edge full width
* **Height**: 44px (comfortable, breathing desktop-taskbar height similar to Cinnamon/Windows)
* **Visual Style**: Dark translucent frosted glass (`rgba(16, 20, 28, 0.84)`) with soft blur, high contrast readability, zero outer shadow, and an ultra-subtle 1px top border
* **Typography**: Modern typography styled with the **Asam font**, with standard icon and system font fallbacks
* **Icons**: **Papirus-Dark** icon theme for all application icons (22px) and unified symbolic system icons

---

## 📋 Layout Sections & Behavior

### 1. Left Section
* **Current Workspace (`niri/workspaces`)**:
  * Displays **only** the active workspace number (`1`, `2`, etc.) in a refined glass badge.
  * Inactive workspaces are hidden (`"current-only": true`).
* **Open Applications (`wlr/taskbar`)**:
  * Directly replaces the active window text title with **application icons**.
  * Styled with **Papirus-Dark** icons at **22px** with balanced 32px hitboxes.
  * Configured with `"all-outputs": true` to reliably detect all running desktop applications (Firefox, Terminal, Telegram, etc.).
  * **Distinguishable states**:
    * **Running / Inactive app**: Subtle bottom indicator underline (`border-bottom: 2px solid rgba(255, 255, 255, 0.25)`).
    * **Hover app**: Translucent frosted glass highlight tile with brighter underline.
    * **Active focused app**: Distinct illuminated frosted glass background tile with an elegant frosted ice-blue accent underline (`rgba(186, 230, 253, 0.95)`).

### 2. Far Right Section: System Information (Reversed Order)
The entire system information sequence is arranged in full **right-to-left reversed order**, placing the desktop clock at the bottom-right corner:
1. **Microphone (`pulseaudio#microphone`)**: Microphone icon and volume level (`   {volume}%` e.g. `   100%` or `   Muted`).
2. **Volume (`pulseaudio`)**: Speaker icon and volume percentage (`{icon}   {volume}%` e.g. `   75%` or `   Muted`).
3. **RAM (`memory`)**: Chip icon and memory usage (`   {used:0.1f}G` e.g. `   6.2G`).
4. **Free Disk Space (`disk`)**: Hard drive icon and free space (`   {specific_free:0.0f}G` e.g. `   124G`).
5. **Keyboard Layout (`niri/language`)**: Keyboard icon and layout indicator (`   EN`, `   DE`, `   FA`).
6. **Wi-Fi (`network`)**: Status icon and signal strength (`   {signalStrength}%` / `󰈀   Eth` / `󰤮   Off`).
7. **Battery (`battery`)**: Dynamic battery glyph and percentage (`{icon}   {capacity}%` e.g. `   87%`).
8. **Clock (`clock`)**: Primary desktop anchor at the far right corner (`   {:%H:%M}`) in bold Asam font.

All system modules share a comfortable 3-space icon-to-value gap and unified module spacing for a clean, coherent desktop system tray.

---

## 🚀 How to Launch & Reload Waybar

### Option A: Launch from `~/bar`
```bash
waybar -c ~/bar/config.jsonc -s ~/bar/style.css &
```

### Option B: Launch from standard config path (`~/.config/waybar`)
```bash
waybar &
```

### Reloading Waybar (Live configuration reload)
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
