#!/usr/bin/env bash
# Install Flash for the current user on Linux (no root needed), or remove it again.
#   bash install_linux.sh             install from ./Flash (release tarball) or dist/Flash (source tree)
#   bash install_linux.sh --uninstall
#
# Installs to ~/.local/opt/flash, adds the 'flash-esp' command to ~/.local/bin,
# and adds a menu entry with an icon.
set -euo pipefail

APP_DIR="$HOME/.local/opt/flash"
BIN="$HOME/.local/bin/flash-esp"
DESKTOP="$HOME/.local/share/applications/flash-esp.desktop"
ICON="$HOME/.local/share/icons/hicolor/256x256/apps/flash-esp.png"

refresh_menus() {
    command -v update-desktop-database >/dev/null && update-desktop-database "$HOME/.local/share/applications" || true
    command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q "$HOME/.local/share/icons/hicolor" || true
}

if [ "${1:-}" = "--uninstall" ]; then
    rm -rf "$APP_DIR" "$BIN" "$DESKTOP" "$ICON"
    refresh_menus
    echo "Flash removed. (Settings are kept in ~/.config/Gueni/Flash.conf)"
    exit 0
fi

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC=""
for candidate in "$HERE/Flash" "$HERE/../dist/Flash"; do
    if [ -x "$candidate/Flash" ]; then SRC="$(cd "$candidate" && pwd)"; break; fi
done
[ -n "$SRC" ] || { echo "Flash build not found. Run 'bash scripts/build.sh' first."; exit 1; }

echo "Installing Flash from $SRC ..."
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR" "$(dirname "$BIN")" "$(dirname "$DESKTOP")" "$(dirname "$ICON")"
cp -a "$SRC/." "$APP_DIR/"
ln -sf "$APP_DIR/Flash" "$BIN"

logo="$(find "$APP_DIR" -path '*flash/assets/logo.png' | head -n1)"
[ -n "$logo" ] && cp "$logo" "$ICON"

cat > "$DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=Flash
GenericName=ESP flashing toolkit
Comment=Flash, inspect and secure ESP32 / ESP8266 chips
Exec=$APP_DIR/Flash
Icon=flash-esp
Terminal=false
Categories=Development;Electronics;
Keywords=esp32;esp8266;esptool;firmware;efuse;
StartupWMClass=Flash
EOF
refresh_menus

echo "Installed. Start it from the application menu or run: flash-esp"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "NOTE: add ~/.local/bin to your PATH to use the flash-esp command." ;; esac
if ! id -nG "$USER" | grep -qwE "dialout|uucp"; then
    echo "NOTE: for serial port access run: sudo usermod -aG dialout \$USER  (then log out and back in)"
fi
