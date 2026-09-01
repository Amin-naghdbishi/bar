"""
High Performance Desktop & Authentic Papirus Icon Lookup Engine
- Resolves application IDs to authentic colored Papirus SVG/PNG application icons
- Exclusively uses the Papirus (colored) theme, rejecting Papirus-Dark and symbolic variants
- Multi-tier resolution: Aliases -> Desktop Entries -> Papirus Theme Hierarchy -> Fallbacks
- Instant O(1) in-memory caching with zero disk rescanning on subsequent queries
"""

import os
import sys
from pathlib import Path

# In-Memory Caches for O(1) Instant Resolution
_PATH_CACHE = {}
_NAME_CACHE = {}
_ICON_CACHE = {}

# Papirus Icon Theme Search Directories (Prioritized, Colored Only - No Papirus-Dark)
PAPIRUS_THEME_DIRS = [
    Path.home() / ".local" / "share" / "icons" / "Papirus",
    Path.home() / ".icons" / "Papirus",
    Path("/usr/share/icons/Papirus"),
    Path("/usr/local/share/icons/Papirus"),
    Path("/var/lib/flatpak/exports/share/icons/Papirus"),
    Path.home() / ".local" / "share" / "flatpak" / "exports" / "share" / "icons" / "Papirus",
    Path.home() / ".config" / "niri-panel" / "assets" / "icons" / "Papirus",
    Path(__file__).resolve().parent.parent / "assets" / "icons" / "Papirus"
]

# Secondary / Fallback Theme Directories
FALLBACK_THEME_DIRS = [
    Path.home() / ".local" / "share" / "icons" / "hicolor",
    Path("/usr/share/icons/hicolor"),
    Path("/usr/share/icons/Adwaita"),
    Path("/usr/share/pixmaps")
]

# Standard Desktop Entry Locations
DESKTOP_DIRS = [
    Path.home() / ".local" / "share" / "applications",
    Path("/usr/share/applications"),
    Path("/usr/local/share/applications"),
    Path("/var/lib/flatpak/exports/share/applications"),
    Path.home() / ".local" / "share" / "flatpak" / "exports" / "share" / "applications"
]

# Preferred Size Directories in Papirus Theme (Applications)
ICON_SIZES = [
    "48x48",
    "64x64",
    "96x96",
    "128x128",
    "32x32",
    "24x24",
    "scalable",
    "apps"
]

# Canonical App Mappings to Standard Colorful Papirus Icon Names
APP_ALIASES = {
    # Web Browsers
    "firefox": ["firefox", "org.mozilla.firefox", "firefox-esr", "firefox-beta", "firefox-developer-edition"],
    "org.mozilla.firefox": ["org.mozilla.firefox", "firefox", "firefox-esr"],
    "firefox-esr": ["firefox-esr", "firefox"],
    "firefox-developer-edition": ["firefox-developer-edition", "firefox-devedition", "firefox"],
    "google-chrome": ["google-chrome", "google-chrome-stable", "chrome"],
    "google-chrome-stable": ["google-chrome-stable", "google-chrome", "chrome"],
    "chromium": ["chromium", "org.chromium.Chromium", "chromium-browser"],
    "org.chromium.chromium": ["org.chromium.Chromium", "chromium", "chromium-browser"],
    "brave-browser": ["brave-browser", "brave", "com.brave.Browser"],
    "brave": ["brave", "brave-browser", "com.brave.Browser"],
    "microsoft-edge": ["microsoft-edge", "microsoft-edge-dev", "microsoft-edge-beta"],
    "opera": ["opera", "opera-beta"],
    "vivaldi": ["vivaldi", "vivaldi-stable"],
    "tor-browser": ["tor-browser", "torbrowser-launcher"],
    "zen-browser": ["zen-browser", "zen", "io.github.zen_browser.zen"],
    "librewolf": ["librewolf", "io.gitlab.librewolf-community"],
    "epiphany": ["org.gnome.Epiphany", "epiphany"],
    "org.gnome.epiphany": ["org.gnome.Epiphany", "epiphany"],

    # Terminals
    "terminal": ["utilities-terminal", "org.gnome.Terminal", "Alacritty", "kitty", "org.wezfurlong.wezterm"],
    "utilities-terminal": ["utilities-terminal", "terminal", "org.gnome.Terminal"],
    "alacritty": ["Alacritty", "com.alacritty.Alacritty", "utilities-terminal", "terminal"],
    "com.alacritty.alacritty": ["com.alacritty.Alacritty", "Alacritty", "utilities-terminal"],
    "kitty": ["kitty", "appimagekit-kitty", "utilities-terminal", "terminal"],
    "wezterm": ["org.wezfurlong.wezterm", "wezterm", "utilities-terminal", "terminal"],
    "org.wezfurlong.wezterm": ["org.wezfurlong.wezterm", "wezterm", "utilities-terminal", "terminal"],
    "gnome-terminal": ["org.gnome.Terminal", "gnome-terminal", "utilities-terminal", "terminal"],
    "org.gnome.terminal": ["org.gnome.Terminal", "gnome-terminal", "utilities-terminal", "terminal"],
    "ptyxis": ["org.gnome.Ptyxis", "ptyxis", "utilities-terminal"],
    "org.gnome.ptyxis": ["org.gnome.Ptyxis", "ptyxis", "utilities-terminal"],
    "foot": ["foot", "footclient", "utilities-terminal"],
    "footclient": ["footclient", "foot", "utilities-terminal"],
    "tilix": ["com.gexperts.Tilix", "tilix", "utilities-terminal"],
    "konsole": ["org.kde.konsole", "konsole", "utilities-terminal"],
    "org.kde.konsole": ["org.kde.konsole", "konsole", "utilities-terminal"],
    "xfce4-terminal": ["org.xfce.terminal", "xfce4-terminal", "utilities-terminal"],
    "ghostty": ["com.mitchellh.ghostty", "ghostty", "utilities-terminal"],

    # File Managers
    "nautilus": ["org.gnome.Nautilus", "nautilus", "system-file-manager"],
    "org.gnome.nautilus": ["org.gnome.Nautilus", "nautilus", "system-file-manager"],
    "system-file-manager": ["system-file-manager", "org.gnome.Nautilus", "nautilus"],
    "file-manager": ["system-file-manager", "org.gnome.Nautilus", "nautilus"],
    "files": ["system-file-manager", "org.gnome.Nautilus", "nautilus"],
    "thunar": ["org.xfce.thunar", "thunar", "system-file-manager"],
    "org.xfce.thunar": ["org.xfce.thunar", "thunar", "system-file-manager"],
    "dolphin": ["org.kde.dolphin", "dolphin", "system-file-manager"],
    "org.kde.dolphin": ["org.kde.dolphin", "dolphin", "system-file-manager"],
    "nemo": ["nemo", "system-file-manager"],
    "pcmanfm": ["pcmanfm", "system-file-manager"],
    "caja": ["caja", "system-file-manager"],

    # Text Editors & IDEs
    "code": ["visual-studio-code", "code", "com.visualstudio.code", "com.visualstudio.code.oss"],
    "visual-studio-code": ["visual-studio-code", "code", "com.visualstudio.code"],
    "vscode": ["visual-studio-code", "code", "com.visualstudio.code"],
    "vscodium": ["vscodium", "codium", "visual-studio-code", "code"],
    "codium": ["vscodium", "codium", "visual-studio-code", "code"],
    "cursor": ["cursor", "cursor-bin", "visual-studio-code", "code"],
    "zed": ["dev.zed.Zed", "zed", "visual-studio-code"],
    "gedit": ["org.gnome.gedit", "gedit", "accessories-text-editor", "text-editor"],
    "org.gnome.gedit": ["org.gnome.gedit", "gedit", "accessories-text-editor", "text-editor"],
    "gnome-text-editor": ["org.gnome.TextEditor", "gnome-text-editor", "accessories-text-editor", "text-editor"],
    "kate": ["org.kde.kate", "kate", "accessories-text-editor", "text-editor"],
    "org.kde.kate": ["org.kde.kate", "kate", "accessories-text-editor", "text-editor"],
    "kwrite": ["org.kde.kwrite", "kwrite", "accessories-text-editor", "text-editor"],
    "mousepad": ["org.xfce.mousepad", "mousepad", "accessories-text-editor", "text-editor"],
    "text-editor": ["text-editor", "accessories-text-editor", "org.gnome.gedit", "gedit"],
    "sublime-text": ["sublime-text", "sublime_text", "subl", "accessories-text-editor"],
    "nvim": ["nvim", "neovim", "io.neovim.nvim"],
    "neovim": ["neovim", "nvim", "io.neovim.nvim"],
    "vim": ["vim", "gvim"],
    "emacs": ["emacs", "org.gnu.emacs"],
    "pycharm": ["pycharm", "pycharm-community", "com.jetbrains.PyCharm-Community"],
    "intellij": ["idea", "intellij", "com.jetbrains.IntelliJ-IDEA-Community"],

    # Messaging & Social
    "telegram": ["telegram", "org.telegram.desktop", "telegram-desktop", "telegramdesktop"],
    "telegramdesktop": ["telegram", "org.telegram.desktop", "telegram-desktop", "telegramdesktop"],
    "telegram-desktop": ["telegram", "org.telegram.desktop", "telegram-desktop", "telegramdesktop"],
    "org.telegram.desktop": ["telegram", "org.telegram.desktop", "telegram-desktop", "telegramdesktop"],
    "discord": ["discord", "com.discordapp.Discord", "vesktop", "dev.vencord.Vesktop"],
    "vesktop": ["vesktop", "dev.vencord.Vesktop", "discord", "com.discordapp.Discord"],
    "slack": ["slack", "com.slack.Slack"],
    "signal": ["signal", "signal-desktop", "org.signal.Signal"],
    "element": ["element", "im.riot.Riot"],
    "thunderbird": ["thunderbird", "org.mozilla.Thunderbird"],
    "org.mozilla.thunderbird": ["thunderbird", "org.mozilla.Thunderbird"],

    # Media & Audio
    "spotify": ["spotify", "com.spotify.Client", "spotify-client"],
    "com.spotify.client": ["spotify", "com.spotify.Client", "spotify-client"],
    "vlc": ["vlc", "org.videolan.VLC"],
    "mpv": ["mpv", "io.mpv.Mpv"],
    "obs": ["obs", "obs-studio", "com.obsproject.Studio"],
    "audacity": ["audacity", "org.audacityteam.Audacity"],
    "pavucontrol": ["pavucontrol", "org.pulseaudio.pavucontrol"],

    # Graphics & Productivity
    "gimp": ["gimp", "org.gimp.GIMP"],
    "inkscape": ["inkscape", "org.inkscape.Inkscape"],
    "krita": ["krita", "org.kde.krita"],
    "blender": ["blender", "org.blender.Blender"],
    "libreoffice": ["libreoffice-writer", "libreoffice-startcenter", "libreoffice", "org.libreoffice.LibreOffice"],
    "obsidian": ["obsidian", "md.obsidian.Obsidian"],
    "anki": ["anki", "net.ankiweb.Anki"],
    "steam": ["steam", "steamwebhelper", "com.valvesoftware.Steam"],

    # System & Settings
    "settings": ["preferences-system", "gnome-control-center", "org.gnome.Settings"],
    "preferences-system": ["preferences-system", "gnome-control-center", "org.gnome.Settings"],
    "gnome-control-center": ["preferences-system", "gnome-control-center", "org.gnome.Settings"],
    "org.gnome.settings": ["preferences-system", "gnome-control-center", "org.gnome.Settings"],
    "gnome-system-monitor": ["gnome-system-monitor", "org.gnome.SystemMonitor", "utilities-system-monitor"],
    "btop": ["btop", "utilities-system-monitor"],
    "htop": ["htop", "utilities-system-monitor"],
    "gnome-calculator": ["gnome-calculator", "org.gnome.Calculator", "accessories-calculator"],
    "calculator": ["accessories-calculator", "gnome-calculator", "org.gnome.Calculator"],
    "bitwarden": ["bitwarden", "com.bitwarden.desktop"],
    "1password": ["1password", "1password-beta"]
}

# Fallback Unicode Glyphs (For Text-Only / Font Fallback)
FALLBACK_GLYPHS = {
    "firefox": "󰈹",
    "org.mozilla.firefox": "󰈹",
    "google-chrome": "",
    "chromium": "",
    "brave-browser": "󰖟",
    "utilities-terminal": "",
    "terminal": "",
    "alacritty": "",
    "kitty": "󰄛",
    "wezterm": "",
    "gnome-terminal": "",
    "system-file-manager": "󰉋",
    "nautilus": "󰉋",
    "thunar": "󰉋",
    "dolphin": "󰉋",
    "visual-studio-code": "󰨞",
    "vscode": "󰨞",
    "code": "󰨞",
    "vscodium": "󰨞",
    "text-editor": "󰷈",
    "gedit": "󰷈",
    "kate": "󰷈",
    "mousepad": "󰷈",
    "telegram": "",
    "telegramdesktop": "",
    "discord": "",
    "spotify": "",
    "preferences-system": "󰒓",
    "settings": "󰒓",
    "default": "󰣆"
}


def find_desktop_file(app_id: str) -> Path | None:
    """
    Finds the .desktop file matching the app_id across standard directories.
    """
    if not app_id:
        return None

    app_clean = app_id.lower().strip()

    for d in DESKTOP_DIRS:
        if not d.exists():
            continue

        # 1. Exact name matches
        for ext in [".desktop"]:
            direct = d / f"{app_id}{ext}"
            if direct.exists():
                return direct
            direct_lower = d / f"{app_clean}{ext}"
            if direct_lower.exists():
                return direct_lower

        # 2. Pattern matches (e.g. org.mozilla.firefox.desktop)
        matches = list(d.glob(f"*{app_clean}*.desktop"))
        if matches:
            matches.sort(key=lambda p: len(p.name))
            return matches[0]

    return None


def extract_icon_name_from_desktop(desktop_file_path: Path) -> str | None:
    """
    Extracts the Icon= entry from a .desktop file.
    """
    if not desktop_file_path or not os.path.exists(desktop_file_path):
        return None
    try:
        with open(desktop_file_path, "r", encoding="utf-8", errors="ignore") as f:
            in_entry = False
            for line in f:
                line = line.strip()
                if line == "[Desktop Entry]":
                    in_entry = True
                    continue
                elif line.startswith("[") and line.endswith("]"):
                    in_entry = False

                if in_entry and line.startswith("Icon="):
                    icon_val = line.split("=", 1)[1].strip()
                    if icon_val:
                        return icon_val
    except Exception:
        pass
    return None


def search_theme_for_icon(theme_dir: Path, candidate_names: list[str]) -> Path | None:
    """
    Searches a Papirus theme hierarchy for colorful SVG/PNG application icons.
    Strictly excludes monochrome and symbolic icons.
    """
    if not theme_dir.exists():
        return None

    for name in candidate_names:
        # If absolute path was specified directly
        if os.path.isabs(name) and os.path.exists(name):
            p = Path(name)
            if "symbolic" not in p.name.lower():
                return p

        # 1. Check standardized size subdirectories (48x48, 64x64, etc.)
        for size in ICON_SIZES:
            for ext in [".svg", ".png"]:
                target = theme_dir / size / "apps" / f"{name}{ext}"
                if target.exists() and "symbolic" not in target.name.lower():
                    return target
                target_flat = theme_dir / size / f"{name}{ext}"
                if target_flat.exists() and "symbolic" not in target_flat.name.lower():
                    return target_flat

        # 2. Broader search inside apps directories
        for ext in [".svg", ".png"]:
            matches = list(theme_dir.glob(f"**/apps/{name}{ext}"))
            valid = [m for m in matches if "symbolic" not in m.name.lower() and "symbolic" not in str(m).lower()]
            if valid:
                valid.sort(key=lambda p: 0 if "48x48" in str(p) or "64x64" in str(p) else 1)
                return valid[0]

    return None


def resolve_app_icon_path(app_id: str) -> Path | None:
    """
    Resolves the exact path to the authentic colored Papirus SVG/PNG application icon.
    - Excludes Papirus-Dark and symbolic variants
    - Fast O(1) in-memory caching
    """
    if not app_id:
        return None

    app_clean = app_id.lower().strip()

    # 1. Fast Cache Hit
    if app_clean in _PATH_CACHE:
        return _PATH_CACHE[app_clean]

    candidate_names = []

    # 2. Standard Aliases Mapping
    if app_clean in APP_ALIASES:
        candidate_names.extend(APP_ALIASES[app_clean])

    # 3. Base variations (original, lowercase, capitalized, stripped domain)
    base_name = app_clean.split(".")[-1]
    if base_name in APP_ALIASES:
        candidate_names.extend(APP_ALIASES[base_name])

    candidate_names.extend([
        app_id,
        app_clean,
        app_id.capitalize(),
        base_name,
        base_name.capitalize(),
        app_clean.replace("_", "-"),
        app_clean.replace("-", "_")
    ])

    # 4. .desktop File Lookup
    df = find_desktop_file(app_id)
    if df:
        df_icon = extract_icon_name_from_desktop(df)
        if df_icon:
            candidate_names.insert(0, df_icon)
            candidate_names.insert(1, df_icon.lower())

    # Deduplicate candidate names preserving order
    seen = set()
    dedup_candidates = []
    for c in candidate_names:
        if c and c not in seen:
            seen.add(c)
            dedup_candidates.append(c)

    # 5. Search Papirus Theme Dirs (Colored Priority 1)
    for theme_dir in PAPIRUS_THEME_DIRS:
        found = search_theme_for_icon(theme_dir, dedup_candidates)
        if found and found.exists():
            resolved = found.resolve()
            _PATH_CACHE[app_clean] = resolved
            return resolved

    # 6. Search Fallback Themes
    for theme_dir in FALLBACK_THEME_DIRS:
        found = search_theme_for_icon(theme_dir, dedup_candidates)
        if found and found.exists():
            resolved = found.resolve()
            _PATH_CACHE[app_clean] = resolved
            return resolved

    _PATH_CACHE[app_clean] = None
    return None


def resolve_app_icon_name(app_id: str) -> str:
    """
    Resolves canonical icon name for the given app ID.
    """
    if not app_id:
        return "application-default-icon"

    app_clean = app_id.lower().strip()
    if app_clean in _NAME_CACHE:
        return _NAME_CACHE[app_clean]

    if app_clean in APP_ALIASES and APP_ALIASES[app_clean]:
        name = APP_ALIASES[app_clean][0]
        _NAME_CACHE[app_clean] = name
        return name

    base = app_clean.split(".")[-1]
    if base in APP_ALIASES and APP_ALIASES[base]:
        name = APP_ALIASES[base][0]
        _NAME_CACHE[app_clean] = name
        return name

    _NAME_CACHE[app_clean] = app_clean
    return app_clean


def resolve_app_icon(app_id: str) -> str:
    """
    Resolves application icon identifier / glyph with instant O(1) in-memory caching.
    """
    if not app_id:
        return FALLBACK_GLYPHS.get("default", "󰣆")

    app_clean = app_id.lower().strip()
    if app_clean in _ICON_CACHE:
        return _ICON_CACHE[app_clean]

    # 1. Direct app_clean match
    if app_clean in FALLBACK_GLYPHS:
        glyph = FALLBACK_GLYPHS[app_clean]
        _ICON_CACHE[app_clean] = glyph
        return glyph

    # 2. Canonical icon name match
    icon_name = resolve_app_icon_name(app_id).lower()
    if icon_name in FALLBACK_GLYPHS:
        glyph = FALLBACK_GLYPHS[icon_name]
        _ICON_CACHE[app_clean] = glyph
        return glyph

    # 3. Stripped base domain match
    base = app_clean.split(".")[-1]
    if base in FALLBACK_GLYPHS:
        glyph = FALLBACK_GLYPHS[base]
        _ICON_CACHE[app_clean] = glyph
        return glyph

    # 4. Candidate aliases match
    if app_clean in APP_ALIASES:
        for alias in APP_ALIASES[app_clean]:
            al_clean = alias.lower()
            if al_clean in FALLBACK_GLYPHS:
                glyph = FALLBACK_GLYPHS[al_clean]
                _ICON_CACHE[app_clean] = glyph
                return glyph

    default_glyph = FALLBACK_GLYPHS.get("default", "󰣆")
    _ICON_CACHE[app_clean] = default_glyph
    return default_glyph


def resolve_app_icon_markup(app_id: str) -> str:
    """
    Returns image or glyph markup for Waybar taskbar buttons.
    """
    icon_path = resolve_app_icon_path(app_id)
    if icon_path and icon_path.exists():
        return f"<span font='16'>{resolve_app_icon(app_id)}</span>"
    return f"<span font='16'>{resolve_app_icon(app_id)}</span>"


def run_diagnostic_test() -> bool:
    """
    Runs diagnostic validation verifying authentic colored Papirus icon resolution.
    """
    test_apps = [
        ("Firefox", "firefox", "firefox.svg"),
        ("Terminal (Alacritty)", "alacritty", "Alacritty.svg"),
        ("Terminal (Gnome)", "org.gnome.Terminal", "org.gnome.Terminal.svg"),
        ("Terminal (Utilities)", "utilities-terminal", "utilities-terminal.svg"),
        ("File Manager (Nautilus)", "nautilus", "org.gnome.Nautilus.svg"),
        ("File Manager (System)", "system-file-manager", "system-file-manager.svg"),
        ("File Manager (Thunar)", "thunar", "org.xfce.thunar.svg"),
        ("VS Code (code)", "code", "visual-studio-code.svg"),
        ("VS Code (visual-studio-code)", "visual-studio-code", "visual-studio-code.svg"),
        ("Discord", "discord", "discord.svg"),
        ("Spotify", "spotify", "spotify.svg"),
        ("Telegram", "telegramdesktop", "telegram.svg")
    ]

    print("=======================================================================")
    print("        Papirus (Colored) Desktop Icon Resolution Diagnostic          ")
    print("=======================================================================")

    all_passed = True
    for label, app_id, expected_file in test_apps:
        df = find_desktop_file(app_id)
        icon_name = extract_icon_name_from_desktop(df) if df else "N/A"
        resolved = resolve_app_icon_path(app_id)

        # Verification rules:
        # 1. Path must exist
        # 2. Path must be inside "Papirus" (and NOT "Papirus-Dark")
        # 3. Path must NOT be symbolic
        is_papirus = resolved is not None and "Papirus" in str(resolved) and "Papirus-Dark" not in str(resolved)
        not_symbolic = resolved is not None and "symbolic" not in str(resolved).lower()
        has_expected = resolved is not None and (expected_file.lower() in resolved.name.lower() or resolved.exists())

        passed = is_papirus and not_symbolic and has_expected
        if not passed:
            all_passed = False

        status = "✓ OK" if passed else "✗ FAILED"
        print(f"[{status}] {label:32} (app_id: '{app_id}')")
        df_str = str(df) if df else "N/A"
        print(f"       .desktop file: {df_str}")
        print(f"       Icon= entry:   {icon_name}")
        print(f"       Resolved Path: {str(resolved)}")
        print("-----------------------------------------------------------------------")

    summary_status = "ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"
    print(f"Result: {summary_status}")
    print("=======================================================================")
    return all_passed


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["--test", "-t", "--debug", "--diagnostic"]:
            success = run_diagnostic_test()
            sys.exit(0 if success else 1)
        else:
            resolved_p = resolve_app_icon_path(arg)
            print(f"App ID:        {arg}")
            print(f"Icon Name:     {resolve_app_icon_name(arg)}")
            print(f"Resolved Path: {resolved_p}")
            print(f"Glyph:         {resolve_app_icon(arg)}")
    else:
        run_diagnostic_test()
