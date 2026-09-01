# Professional Niri Waybar Desktop Panel

A modern, highly modular desktop shell panel and taskbar engineered specifically for the **Niri Wayland Compositor** on Arch Linux.

Inspired by the polished aesthetics of **Windows 11**, the practical desktop workflow of **Cinnamon**, and the clean minimalism of the **Omarchy bar philosophy**, this project turns Waybar into a complete, professional Linux desktop shell component.

---

## 🌟 Key Design Philosophy: The Clean Bar Rule

The main bar is strictly optimized for high visual clarity and zero clutter:
- ❌ **NO** raw CPU/RAM percentage numbers
- ❌ **NO** battery percentages or noisy volume percentages on the main panel
- ❌ **NO** long truncated window title labels
- ✔️ **Clean, state-aware glyphs and minimal badges ONLY**
- 🖱️ **Rich, interactive popup centers** on click

---

## 🖥️ Layout Overview

```
+---+-------------------------------------------+-----------------------------------------------+
| 3 |  󰈹 ●●    ●   󰉋   󰨞                       |  18:32   󰕾   󰂱   󰁹   󰋊   EN   󰅃            |
+---+-------------------------------------------+-----------------------------------------------+
 Left              Middle                                            Right
 [Workspace]     [Pinned & Running Apps]         [Clock] [Audio] [BT] [Power] [Disk] [KB] [Tray]
```

### 1. Minimal Workspace Indicator (Left)
- Shows **ONLY the active Niri workspace number** (e.g. `1`, `2`, `3`).
- Larger font size (15px bold) housed in a crisp frosted glass badge.
- Subtle transition feedback upon workspace switching.
- Workspace navigation is handled naturally by Niri keybindings (`Mod+1..9`, `Mod+Wheel`).

### 2. Application Taskbar & Window Management (Middle)
- **Pinned Applications**: Quick access to essential apps (Firefox, Terminal, Files, Editor).
  - Closed: Click launches the application.
  - Running: Click focuses the application.
- **Running Window Indicators**: Detects all open windows using **Niri IPC** (`niri msg -j windows`).
  - Single window: `󰈹 ●`
  - Multiple windows: `󰈹 ●●` or `󰈹 ●●●`
- **Window Grouping Selector**: Clicking an app with multiple windows opens an interactive window selector popup (e.g. `ChatGPT`, `YouTube`, `Documentation`) with instant focus on click.
- **Right-Click Context Menus**: Full right-click menu for any application:
  - 🗖 Open New Window
  - ✕ Close Window
  - 📌 Pin / Unpin from Taskbar
  - 🚀 Launch at Startup (Autostart toggle)
  - ⏻ Quit Application

### 3. Integrated Control Centers & System Popups (Right)

| Module | Main Bar Representation | Interactive Popup Features |
| :--- | :--- | :--- |
| **Clock** | `18:32` (HH:MM, no icon) | Full date, live seconds clock, interactive month calendar with week numbers, timezone, UTC offset, system uptime. |
| **Audio Center** | `󰕾` Single speaker icon (Muted: `󰝟`) | Combined output volume slider, output audio sink switcher (Speakers, Headphones, HDMI), microphone slider + mic mute toggle + input device switcher, per-app volume streams (Firefox, Discord, Telegram...). |
| **Battery & Power** | `󰁹` Dynamic battery icon (Charging: `󰂄`) | Battery %, time remaining estimate, AC status, Power Profiles (Performance, Balanced, Power Saver), Display Brightness slider, Night Light toggle (Blue light filter), 80% Battery Protection toggle, Power actions (Lock, Sleep, Reboot, Shutdown). |
| **Bluetooth Center** | `󰂯` (Connected: `󰂱`, Off: `󰂲`) | Master Bluetooth ON/OFF toggle, device scanner, connected devices with battery %, paired & available devices list with Connect/Pair/Disconnect. |
| **Storage Center** | `󰋊` Clean disk icon | Root (`/`) and Home (`~`) partition usage bars and percentages, categorized folder breakdown (Pictures, Videos, Music, Downloads, Documents) sorted by largest size first, quick "Open in File Manager" action. |
| **Keyboard Center** | `EN` / `FA` layout badge | Active layout indicator, one-click layout switcher via Niri IPC (`niri msg action switch-layout`), shortcut hints. |
| **System Tray Overflow** | `󰅃` Chevron-up icon | Attached floating tray popup for background applications (Telegram, Discord, Hiddify, Delta Chat, Anki, Steam, etc.). |

---

## 🗂️ Project Structure

```
professional-panel/
├── install.sh                  # Automated installer & dependency manager
├── uninstall.sh                # Clean uninstaller and backup restorer
├── README.md                   # Full documentation & guide
├── .gitignore                  # Gitignore for Linux/Waybar/Python
│
├── waybar/
│   ├── config.jsonc            # Complete Waybar layout configuration
│   └── style.css               # Modern glassmorphism dark stylesheet
│
├── scripts/
│   ├── workspace.py            # Niri IPC workspace stream daemon
│   ├── workspace.sh            # Workspace wrapper launcher
│   ├── taskbar.py              # Niri taskbar engine (pins, dots, grouping)
│   ├── taskbar.sh              # Taskbar wrapper launcher
│   ├── taskbar_action.py       # Taskbar click/menu dispatcher
│   ├── popup_manager.py        # Singleton popup lifecycle manager
│   ├── popup_manager.sh        # Popup manager launcher
│   ├── audio_status.py         # WirePlumber/PipeWire status reporter
│   ├── battery_status.py       # UPower/sysfs battery status reporter
│   ├── bluetooth_status.py     # BlueZ status reporter
│   ├── storage_status.py       # Disk usage reporter
│   ├── keyboard_status.py      # Niri keyboard layout reporter
│   ├── tray.sh                 # Tray overflow launcher
│   └── autostart.sh            # Panel autostart helper
│
├── popup/
│   ├── common/
│   │   ├── base.py             # Layer-shell base window with auto-dismiss
│   │   ├── theme.py            # Color tokens and design constants
│   │   └── styles.css          # Shared GTK3 glassmorphism stylesheet
│   ├── audio/
│   │   ├── audio_popup.py      # Audio Center GUI
│   │   └── backend.py          # PipeWire / WirePlumber backend
│   ├── battery/
│   │   ├── battery_popup.py    # Battery & Power Center GUI
│   │   └── backend.py          # UPower / PowerProfiles / Brightness backend
│   ├── bluetooth/
│   │   ├── bluetooth_popup.py  # Bluetooth Center GUI
│   │   └── backend.py          # BlueZ / bluetoothctl backend
│   ├── storage/
│   │   ├── storage_popup.py    # Storage Center GUI
│   │   └── backend.py          # Disk breakdown backend
│   ├── clock/
│   │   └── clock_popup.py      # Calendar & Time Center GUI
│   ├── keyboard/
│   │   ├── keyboard_popup.py   # Keyboard Layout Center GUI
│   │   └── backend.py          # Niri layout backend
│   ├── tray/
│   │   └── tray_popup.py       # System Tray Overflow GUI
│   └── taskbar/
│       ├── window_menu.py      # Window grouping selector popup
│       └── context_menu.py     # Right-click application context menu
│
├── config/
│   ├── pinned.json             # Pinned applications definition
│   └── settings.json           # General panel preferences
│
└── assets/
    └── icons/                  # Scalable SVG icons
```

---

## 📦 Dependencies

### Arch Linux (Pacman)
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

1. Clone or download the repository:
   ```bash
   git clone https://github.com/Amin-naghdbishi/bar.git ~/.config/niri-panel-repo
   cd ~/.config/niri-panel-repo
   ```

2. Run the automated installer:
   ```bash
   ./install.sh
   ```
   *(To automatically install missing package dependencies on Arch Linux, run `./install.sh -y`)*

3. Add Waybar to your Niri configuration:
   Edit `~/.config/niri/config.kdl` and add:
   ```kdl
   spawn-at-startup "waybar"
   ```

---

## 🔄 Uninstallation

To restore your previous Waybar configuration and clean up all installed files:
```bash
./uninstall.sh
```

---

## ⚙️ Configuration & Customization

### Pinned Applications
Edit `~/.config/niri-panel/config/pinned.json`:
```json
[
  {
    "name": "Firefox",
    "app_id": "firefox",
    "icon": "firefox",
    "exec": "firefox",
    "autostart": false
  },
  {
    "name": "Terminal",
    "app_id": "alacritty",
    "icon": "utilities-terminal",
    "exec": "alacritty",
    "autostart": false
  }
]
```

### Styling & Theme Customization
All styling is modular and uses CSS variables.
- Panel CSS: `~/.config/waybar/style.css`
- Popups CSS: `~/.config/niri-panel/popup/common/styles.css`

Key CSS variables available in `style.css`:
```css
@define-color bg-panel rgba(16, 20, 28, 0.88);
@define-color accent-blue #38bdf8;
@define-color border-panel-top rgba(255, 255, 255, 0.12);
```

---

## 🛡️ Key Features & Compatibility Notes
- **Compositor**: Optimized for **Niri** Wayland compositor with native `niri msg` IPC.
- **Audio**: Full PipeWire / WirePlumber support (`wpctl`) with PulseAudio (`pactl`) fallback.
- **Power**: Compatible with `power-profiles-daemon`, `tlp`, and ACPI sysfs.
- **Popups**: Layer-shell native positioning with automatic dismissal on Escape and click-outside.

---

## 📄 License

MIT License. Designed with passion for the Linux Wayland & Niri ecosystem.
