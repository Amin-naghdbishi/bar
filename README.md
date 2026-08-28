# Linux Mint Cinnamon-Inspired Frosted Glass Waybar for Niri

A polished, desktop-oriented taskbar for [Niri](https://github.com/YaLTeR/niri) inspired by the **Linux Mint Cinnamon** panel usability, redesigned with a modern **transparent glass and soft blur effect**.

---

## 🖥️ Layout Overview

```text
[ 1 ] Active Window Title                  [App Icons] │ [] [20:42] [EN] [124G] [] [6.2G] [ 87%] [] []
└─────── Left Section ───────┘              └─ Apps ──┘ │ └───────────── Far Right System Tray ─────────────┘
```

* **Position**: Bottom edge-to-edge full width
* **Height**: 38px (comfortable, well-proportioned desktop panel)
* **Visual Style**: Transparent frosted glass with soft background blur, subtle translucency, specular rim, and a crisp 1px top border
* **Typography**: Modern typography styled with the **Asam font**, with standard icon and system font fallbacks
* **Active Window Title**: Text only — strictly no application icon next to the active title

---

## 📋 Layout Sections & Behavior

### 1. Left Section
* **Current Workspace (`niri/workspaces`)**:
  * Displays **only** the active workspace number (`1`, `2`, etc.) in a refined glass badge.
  * Inactive workspaces are hidden (`"current-only": true`).
  * Instant reactive updates when switching workspaces.
* **Active Window Title (`niri/window`)**:
  * Displays the focused application/window title in **pure text only**.
  * **Strictly no application icon** is rendered next to the title (e.g. `Firefox` instead of `[Icon] Firefox`).
  * Styled with clean, high-contrast typography in the Asam font.

### 2. Middle/Right Section: Open / Pinned Applications
* **Taskbar (`wlr/taskbar`)**:
  * Linux Mint Cinnamon-inspired grouped application indicators.
  * Consistent **18px** icon sizes with balanced horizontal padding (32px click targets).
  * **Distinguishable states**:
    * **Running / Inactive app**: Subtle bottom indicator underline (`border-bottom: 2px solid rgba(255, 255, 255, 0.22)`).
    * **Hover app**: Translucent frosted glass highlight tile with brighter underline.
    * **Active focused app**: Distinct illuminated frosted glass background tile with an elegant frosted ice-blue accent underline (`rgba(186, 230, 253, 0.95)`).
  * Click to activate/focus, middle-click to close.
  * Separated from the system tray by a subtle 1px translucent glass divider and spacing.

### 3. Far Right Section: System Information
Placed strictly in the requested desktop order:
1. **Wi-Fi (`network`)**: Clean network status glyph (`` / `󰈀` / `󰤮`).
2. **Clock (`clock`)**: Primary desktop anchor formatted as `{:%H:%M}` (e.g. `20:42`) in bold Asam font.
3. **Keyboard Layout (`niri/language`)**: Concise layout indicator (e.g. `EN`, `DE`, `FA`).
4. **Free Disk Space (`disk`)**: Available root partition space formatted as `{specific_free:0.0f}G` (e.g. `124G`).
5. **Home (`custom/home`)**: House icon (``) that opens the home directory on click.
6. **RAM (`memory`)**: Used RAM in gigabytes formatted as `{used:0.1f}G` (e.g. `6.2G`).
7. **Battery (`battery`)**: Dynamic battery glyph and percentage (e.g. ` 87%`) with soft charging/warning/critical states.
8. **Volume (`pulseaudio`)**: Volume icon (`` / `` when muted). Click toggles mute; right-click opens `pavucontrol`; scroll changes volume.
9. **Microphone (`pulseaudio#microphone`)**: Microphone icon (`` / `` when muted). Click toggles mute; scroll adjusts level.

All system items feature interactive desktop applet hover feedback without heavy developer dashboard boxes or oversized cards.

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
