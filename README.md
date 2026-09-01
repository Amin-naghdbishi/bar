# Professional Niri Waybar Desktop Panel

A modern, highly modular desktop shell panel and taskbar engineered specifically for the **Niri Wayland Compositor** on Arch Linux.

Inspired by the polished workflow of **Windows 11**, the reliable simplicity of the **Cinnamon Desktop Panel**, and the clean minimalism of the **Omarchy Bar Philosophy**, this system turns Waybar into a complete, professional Linux desktop shell component.

---

## 🌟 Main Design Principles

### 1. The Clean Bar Philosophy
The main panel stays strictly minimal and clean:
- ❌ **NO** raw CPU/RAM percentage text cluttering the panel
- ❌ **NO** battery percentages or volume numbers on the main bar
- ❌ **NO** long truncated text labels
- ❌ **NO** shared card boxes or glowing neon underlines
- ✔️ **Independent application buttons with centered window indicators underneath**
- 🖱️ **Actual independent floating popup panels** when clicked

### 2. Restrained, Modern Aesthetics
- Dark neutral frosted glass (`rgba(16, 20, 28, 0.86)`)
- Increased 48px panel height with comfortable breathing room
- Independent 38px application buttons with crisp **Papirus-Dark** icons
- Subtle window indicators (dots) directly underneath each running app
- Restrained borders, subtle glass hover tiles, and zero neon/cyberpunk effects

---

## 🖥️ Layout & Module Structure

```
+---+-------------------------------------------+-----------------------------------------------+
| 3 |  [󰈹]   []   [󰉋]   [󰨞]                   |  [^]   [EN]   [󰋊]   [󰁹]   [󰂱]   [󰕾]   18:32       |
|   |  •••    •                                 |                                               |
+---+-------------------------------------------+-----------------------------------------------+
 Left              Middle                                            Right
 [Workspace]     [Independent App Buttons]       [Tray] -> [KB] -> [Disk] -> [Power] -> [BT] -> [Audio] -> [Clock]
```

### 1. Minimal Workspace Indicator (Far Left)
- Shows **ONLY the active Niri workspace number** (e.g. `1`, `2`, `3`).
- 34x34px frosted glass badge with bold typography.
- Workspace navigation is handled naturally by Niri keybindings (`Mod+1..9`, `Mod+Wheel`).

### 2. Independent Application Taskbar Buttons (Middle)
- **Separate Application Buttons**: Each application has its own completely independent button. No shared cards or surrounding group boxes.
- **Papirus Icon Integration**: Uses `Papirus-Dark` system icon lookup.
- **Centered Window Dots Underneath**:
  - 1 window: `•`
  - 2 windows: `• •`
  - 3 windows: `• • •`
  - 4 windows: `• • • •`
  - 5 windows: `• • • • •`
  - 6+ windows: `• • • • • 6`
  - The focused window's dot is highlighted in sky blue (`#38bdf8`), while inactive windows are neutral slate (`#94a3b8`).
- **Window Grouping Selector Popup**: Clicking an application with multiple open windows opens an interactive window selector to focus or close individual windows.
- **Application Context Menu**: Right-clicking opens options to open new window, close window, pin/unpin, toggle autostart, or quit.

### 3. Ordered System Modules & Real Popups (Right)

The right side is ordered as:
**Tray → Keyboard → Storage → Battery/Power → Bluetooth → Audio → Clock (Far Right Edge)**

| Module | Bar Representation | Real Interactive Popup Features |
| :--- | :--- | :--- |
| **System Tray Overflow** | `󰅃` Chevron-up icon | Windows 11-style compact tray attached above the taskbar button for background apps (Telegram, Discord, Hiddify, Delta Chat, Anki, Steam, etc.). |
| **Keyboard Center** | `EN` / `FA` layout badge | Active layout indicator, one-click layout switcher via Niri IPC (`niri msg action switch-layout`), and shortcut hints. |
| **Storage Center** | `󰋊` Disk icon | Root (`/`) and Home (`~`) partition usage bars and percentages, categorized folder breakdown (Downloads, Videos, Pictures, Documents, Music) sorted by largest size first, with quick "Open in File Manager" action. |
| **Battery & Power** | `󰁹` Dynamic battery icon | Battery %, time remaining estimate, AC status, Power Profiles (Performance, Balanced, Power Saver), Display Brightness slider, Night Light toggle, 80% battery protection limit, and quick power actions (Lock, Sleep, Reboot, Shutdown). |
| **Bluetooth Center** | `󰂯` (Connected: `󰂱`, Off: `󰂲`) | Master Bluetooth ON/OFF switch, device scanner, connected devices with battery %, and paired/available device connection manager. |
| **Audio Center** | `󰕾` Single speaker icon | Master output volume slider with %, audio output device switcher (Speakers, Headphones, HDMI), microphone slider + mute toggle, input device switcher, and per-app audio stream volume controls. |
| **Clock** *(Far Edge)* | `18:32` (HH:MM) | Large digital clock with live seconds, full formatted date, interactive month calendar with week numbers, timezone, and system uptime. |

---

## 🪟 Real Interactive Popup Windows

Clicking any icon opens a **real independent Wayland surface window** powered by GTK3 and `gtk-layer-shell`:
- Solid dark neutral panel surface (`rgba(18, 22, 30, 0.96)`) with 12px rounded corners and subtle border
- Anchored above the taskbar on the right corner
- Fully clickable with real sliders (`GtkScale`), toggles (`GtkSwitch`), buttons, and device lists
- Auto-dismisses on Escape key or clicking outside
- Singleton toggle behavior (clicking the icon again closes the popup)

---

## 📦 Dependencies (Arch Linux)

```bash
sudo pacman -S --needed \
    waybar \
    python \
    python-gobject \
    gtk3 \
    gtk-layer-shell \
    pipewire \
    wireplumber \
    bluez-utils \
    upower \
    brightnessctl \
    wlsunset \
    ttf-nerd-fonts-symbols \
    papirus-icon-theme
```

---

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Amin-naghdbishi/bar.git ~/.config/niri-panel-repo
   cd ~/.config/niri-panel-repo
   ```

2. Run the installer:
   ```bash
   ./install.sh -y
   ```

3. Add Waybar to your Niri configuration:
   Edit `~/.config/niri/config.kdl` and add:
   ```kdl
   spawn-at-startup "waybar"
   ```

---

## 🔄 Uninstallation

To cleanly restore your previous Waybar configuration:
```bash
./uninstall.sh
```

---

## 📄 License

MIT License. Designed for Wayland and the Niri compositor ecosystem.
