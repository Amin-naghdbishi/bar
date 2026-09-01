"""
High Performance Desktop & Papirus Icon Lookup Engine
- Fast O(1) in-memory cached lookup
- Resolves application IDs to authentic Papirus-style application icons
- Zero disk rescanning on subsequent queries
"""

import os
from pathlib import Path

# In-Memory Cache for O(1) Instant Resolution
_ICON_CACHE = {}

PAPIRUS_APP_ICONS = {
    # Web Browsers
    "firefox": "󰈹",
    "org.mozilla.firefox": "󰈹",
    "firefox-esr": "󰈹",
    "firefox-developer-edition": "󰈹",
    "firefox-nightly": "󰈹",
    "google-chrome": "",
    "google-chrome-stable": "",
    "google-chrome-beta": "",
    "google-chrome-unstable": "",
    "chrome": "",
    "chromium": "",
    "org.chromium.Chromium": "",
    "chromium-browser": "",
    "brave-browser": "󰖟",
    "brave": "󰖟",
    "brave-beta": "󰖟",
    "brave-nightly": "󰖟",
    "com.brave.Browser": "󰖟",
    "microsoft-edge": "󰇩",
    "microsoft-edge-dev": "󰇩",
    "microsoft-edge-beta": "󰇩",
    "edge": "󰇩",
    "opera": "",
    "opera-beta": "",
    "opera-developer": "",
    "vivaldi": "󰖟",
    "vivaldi-stable": "󰖟",
    "vivaldi-snapshot": "󰖟",
    "tor-browser": "󰖟",
    "torbrowser-launcher": "󰖟",
    "zen-browser": "󰖟",
    "zen": "󰖟",
    "io.github.zen_browser.zen": "󰖟",
    "librewolf": "󰈹",
    "io.gitlab.librewolf-community": "󰈹",
    "epiphany": "󰖟",
    "org.gnome.Epiphany": "󰖟",
    "qutebrowser": "󰖟",
    "org.qutebrowser.qutebrowser": "󰖟",
    "floorp": "󰈹",
    "waterfox": "󰈹",

    # Terminals
    "alacritty": "",
    "Alacritty": "",
    "kitty": "󰄛",
    "wezterm": "",
    "org.wezfurlong.wezterm": "",
    "foot": "",
    "footclient": "",
    "gnome-terminal": "",
    "org.gnome.Terminal": "",
    "ptyxis": "",
    "org.gnome.Ptyxis": "",
    "tilix": "",
    "com.gexperts.Tilix": "",
    "konsole": "",
    "org.kde.konsole": "",
    "xterm": "",
    "uxterm": "",
    "terminator": "",
    "xfce4-terminal": "",
    "org.xfce.terminal": "",
    "utilities-terminal": "",
    "ghostty": "",
    "com.mitchellh.ghostty": "",
    "warp-terminal": "",
    "dev.warp.Warp": "",
    "rio": "",
    "tabby": "",
    "hyper": "",
    "guake": "",
    "tilda": "",
    "st": "",
    "urxvt": "",

    # File Managers
    "nautilus": "󰉋",
    "org.gnome.Nautilus": "󰉋",
    "thunar": "󰉋",
    "org.xfce.thunar": "󰉋",
    "dolphin": "󰉋",
    "org.kde.dolphin": "󰉋",
    "nemo": "󰉋",
    "pcmanfm": "󰉋",
    "pcmanfm-qt": "󰉋",
    "caja": "󰉋",
    "system-file-manager": "󰉋",
    "files": "󰉋",
    "krusader": "󰉋",
    "doublecmd": "󰉋",

    # Text Editors & IDEs
    "code": "󰨞",
    "visual-studio-code": "󰨞",
    "vscode": "󰨞",
    "com.visualstudio.code": "󰨞",
    "code-oss": "󰨞",
    "code-insiders": "󰨞",
    "vscodium": "󰨞",
    "codium": "󰨞",
    "com.vscodium.codium": "󰨞",
    "cursor": "󰨞",
    "cursor-bin": "󰨞",
    "zed": "󰨞",
    "dev.zed.Zed": "󰨞",
    "gedit": "󰷈",
    "org.gnome.gedit": "󰷈",
    "gnome-text-editor": "󰷈",
    "org.gnome.TextEditor": "󰷈",
    "kate": "󰷈",
    "org.kde.kate": "󰷈",
    "kwrite": "󰷈",
    "org.kde.kwrite": "󰷈",
    "mousepad": "󰷈",
    "org.xfce.mousepad": "󰷈",
    "leafpad": "󰷈",
    "sublime_text": "󰷈",
    "sublime-text": "󰷈",
    "subl": "󰷈",
    "neovim": "",
    "nvim": "",
    "io.neovim.nvim": "",
    "vim": "",
    "gvim": "",
    "emacs": "",
    "org.gnu.emacs": "",
    "text-editor": "󰷈",
    "pycharm": "󰌠",
    "pycharm-community": "󰌠",
    "pycharm-professional": "󰌠",
    "com.jetbrains.PyCharm-Community": "󰌠",
    "intellij": "󰨞",
    "idea": "󰨞",
    "com.jetbrains.IntelliJ-IDEA-Community": "󰨞",
    "webstorm": "󰨞",
    "clion": "󰨞",
    "goland": "󰨞",
    "rustrover": "󰨞",
    "phpstorm": "󰨞",
    "rider": "󰨞",
    "android-studio": "󰀲",
    "com.google.AndroidStudio": "󰀲",
    "geany": "󰷈",

    # Messaging & Social
    "telegramdesktop": "",
    "org.telegram.desktop": "",
    "telegram-desktop": "",
    "telegram": "",
    "materialgram": "",
    "ayugram": "",
    "discord": "",
    "com.discordapp.Discord": "",
    "vesktop": "",
    "dev.vencord.Vesktop": "",
    "webcord": "",
    "armcord": "",
    "element": "󰭹",
    "im.riot.Riot": "󰭹",
    "deltachat": "󰭹",
    "signal": "󰭹",
    "signal-desktop": "󰭹",
    "org.signal.Signal": "󰭹",
    "slack": "󰒱",
    "com.slack.Slack": "󰒱",
    "whatsapp": "󰭹",
    "whatsapp-for-linux": "󰭹",
    "zoom": "󰕧",
    "us.zoom.Zoom": "󰕧",
    "teams": "󰒱",
    "teams-for-linux": "󰒱",
    "mattermost": "󰭹",
    "thunderbird": "󰇮",
    "org.mozilla.Thunderbird": "󰇮",
    "betterbird": "󰇮",
    "geary": "󰇮",
    "mailspring": "󰇮",
    "hexchat": "󰭹",

    # Media & Audio
    "spotify": "",
    "spotify-launcher": "",
    "com.spotify.Client": "",
    "spotube": "",
    "vlc": "󰕼",
    "org.videolan.VLC": "󰕼",
    "mpv": "",
    "io.mpv.Mpv": "",
    "celluloid": "",
    "clapper": "",
    "audacity": "󰓃",
    "org.audacityteam.Audacity": "󰓃",
    "obs": "󰐌",
    "obs-studio": "󰐌",
    "com.obsproject.Studio": "󰐌",
    "kdenlive": "󰕼",
    "handbrake": "󰕼",
    "rhythmbox": "󰎆",
    "audacious": "󰎆",
    "amberol": "󰎆",
    "pavucontrol": "󰕾",
    "org.pulseaudio.pavucontrol": "󰕾",
    "easyeffects": "󰕾",
    "helvum": "󰕾",
    "qpwgraph": "󰕾",

    # Graphics & Productivity
    "gimp": "",
    "org.gimp.GIMP": "",
    "inkscape": "",
    "org.inkscape.Inkscape": "",
    "krita": "",
    "org.kde.krita": "",
    "blender": "󰂫",
    "org.blender.Blender": "󰂫",
    "darktable": "󰄄",
    "rawtherapee": "󰄄",
    "aseprite": "",
    "pixelorama": "",
    "drawio": "󰏆",
    "figma-linux": "󰏆",
    "libreoffice": "󰏆",
    "libreoffice-writer": "󰏆",
    "libreoffice-calc": "󰏆",
    "libreoffice-impress": "󰏆",
    "soffice.bin": "󰏆",
    "org.libreoffice.LibreOffice": "󰏆",
    "onlyoffice": "󰏆",
    "onlyoffice-desktopeditors": "󰏆",
    "wps": "󰏆",
    "obsidian": "󱓧",
    "md.obsidian.Obsidian": "󱓧",
    "logseq": "󱓧",
    "joplin": "󱓧",
    "notion-app": "󱓧",
    "simplenote": "󱓧",
    "anki": "󰠮",
    "net.ankiweb.Anki": "󰠮",
    "evince": "󰈦",
    "org.gnome.Evince": "󰈦",
    "okular": "󰈦",
    "zathura": "󰈦",
    "calibre": "󰈦",
    "foliate": "󰈦",
    "xournalpp": "󰈦",

    # Gaming & Emulation
    "steam": "󰓓",
    "steamwebhelper": "󰓓",
    "com.valvesoftware.Steam": "󰓓",
    "heroic": "󰓓",
    "lutris": "󰓓",
    "bottles": "󰓓",
    "prism-launcher": "󰓓",
    "retroarch": "󰓓",
    "pcsx2": "󰓓",
    "rpcs3": "󰓓",
    "dolphin-emu": "󰓓",
    "ryujinx": "󰓓",

    # Settings & Utilities
    "gnome-control-center": "󰒓",
    "systemsettings": "󰒓",
    "settings": "󰒓",
    "preferences-system": "󰒓",
    "org.gnome.Settings": "󰒓",
    "xfce4-settings-manager": "󰒓",
    "gnome-system-monitor": "󰍛",
    "org.gnome.SystemMonitor": "󰍛",
    "btop": "󰍛",
    "htop": "󰍛",
    "bottom": "󰍛",
    "gnome-calculator": "󰃬",
    "org.gnome.Calculator": "󰃬",
    "calculator": "󰃬",
    "gnome-disks": "󰋊",
    "gparted": "󰋊",
    "baobab": "󰋊",
    "bitwarden": "󰞀",
    "com.bitwarden.desktop": "󰞀",
    "1password": "󰞀",
    "keepassxc": "󰞀",
    "hiddify": "󰒄",
    "nekoray": "󰒄",
    "v2rayn": "󰒄",
    "clash-verge": "󰒄",
    "wireshark": "󰒄",
    "virt-manager": "󰢹",
    "virtualbox": "󰢹",
    "gnome-software": "󰏓",
    "discover": "󰏓",
    "pamac-manager": "󰏓",
    "timeshift": "󰒓",
    "bleachbit": "󰒓",
    "file-roller": "󰉋",
    "ark": "󰉋",
    "peazip": "󰉋",
    "loupe": "󰄄",
    "eog": "󰄄",
    "gwenview": "󰄄",
    "imv": "󰄄",
    "swappy": "󰄄",
    "default": "󰣆"
}

DESKTOP_DIRS = [
    Path.home() / ".local" / "share" / "applications",
    Path("/usr/share/applications"),
    Path("/usr/local/share/applications"),
    Path("/var/lib/flatpak/exports/share/applications"),
    Path.home() / ".local" / "share" / "flatpak" / "exports" / "share" / "applications"
]

def resolve_app_icon(app_id):
    """
    Resolves application icon glyph with instant O(1) in-memory caching.
    Supports App IDs, window classes, reverse domains, and .desktop entries.
    """
    if not app_id:
        return PAPIRUS_APP_ICONS["default"]

    app_clean = app_id.lower().strip()

    # 1. Fast Cache Hit
    if app_clean in _ICON_CACHE:
        return _ICON_CACHE[app_clean]

    # 2. Exact Match in Papirus Icons Map
    if app_clean in PAPIRUS_APP_ICONS:
        icon = PAPIRUS_APP_ICONS[app_clean]
        _ICON_CACHE[app_clean] = icon
        return icon

    # 3. Strip reverse-domain prefixes (e.g. org.mozilla.firefox -> firefox)
    base_name = app_clean.split(".")[-1]
    if base_name in PAPIRUS_APP_ICONS:
        icon = PAPIRUS_APP_ICONS[base_name]
        _ICON_CACHE[app_clean] = icon
        return icon

    # 4. Normalized variations (hyphens / underscores)
    normalized = app_clean.replace("_", "-")
    if normalized in PAPIRUS_APP_ICONS:
        icon = PAPIRUS_APP_ICONS[normalized]
        _ICON_CACHE[app_clean] = icon
        return icon

    # 5. Substring match against known icons
    for k, v in PAPIRUS_APP_ICONS.items():
        if len(k) > 3 and (k in app_clean or app_clean in k or k in base_name):
            _ICON_CACHE[app_clean] = v
            return v

    # 6. Desktop Entry Resolution (executed once per unknown app)
    for d in DESKTOP_DIRS:
        if d.exists():
            for df in d.glob(f"*{app_clean}*.desktop"):
                try:
                    with open(df, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith("Icon="):
                                icon_name = line.split("=", 1)[1].strip().lower()
                                if icon_name in PAPIRUS_APP_ICONS:
                                    icon = PAPIRUS_APP_ICONS[icon_name]
                                    _ICON_CACHE[app_clean] = icon
                                    return icon
                                for k, v in PAPIRUS_APP_ICONS.items():
                                    if len(k) > 3 and (k in icon_name or icon_name in k):
                                        _ICON_CACHE[app_clean] = v
                                        return v
                except Exception:
                    pass

    default_icon = PAPIRUS_APP_ICONS["default"]
    _ICON_CACHE[app_clean] = default_icon
    return default_icon
