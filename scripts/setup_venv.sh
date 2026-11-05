#!/usr/bin/env bash
# Create .venv and install Flash's dependencies (Linux / macOS).
#   bash scripts/setup_venv.sh [--dev]
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null || { echo "python3 not found (install python3 and python3-venv)"; exit 1; }

if [ ! -x .venv/bin/python ]; then
    echo "Creating virtual environment in .venv ..."
    "$PYTHON" -m venv .venv
fi
PY=.venv/bin/python

"$PY" -m pip install --upgrade pip
# The wrong 'serial' package breaks pyserial ("module 'serial' has no attribute 'Serial'").
"$PY" -m pip uninstall -y serial >/dev/null 2>&1 || true
REQ=requirements.txt
[ "${1:-}" = "--dev" ] && REQ=requirements-dev.txt
"$PY" -m pip install -r "$REQ"

if [ "$(uname)" = "Linux" ]; then
    if ! id -nG "$USER" | grep -qwE "dialout|uucp"; then
        echo
        echo "NOTE: to access serial ports without sudo run:"
        echo "      sudo usermod -aG dialout \$USER   (then log out and back in)"
    fi
    if ! ldconfig -p 2>/dev/null | grep -q libxcb-cursor; then
        echo "NOTE: Qt needs libxcb-cursor0 on X11:  sudo apt install libxcb-cursor0"
    fi
fi
echo
echo "Done. Run the app with:  .venv/bin/python main.py"
