#!/usr/bin/env bash
# Full Linux build of Flash: venv -> deps -> tests -> PyInstaller -> smoke test -> installable tarball.
#   bash scripts/build.sh [--skip-tests] [--onefile] [--install]
#
#   default    : dist/Flash/ (one folder) -> release/Flash-<v>-linux-<arch>.tar.gz (contains install.sh)
#   --onefile  : single portable binary   -> release/Flash-<v>-linux-<arch>
#   --install  : also install the build for the current user (see scripts/install_linux.sh)
set -euo pipefail
cd "$(dirname "$0")/.."

ONEFILE=0; SKIP_TESTS=0; INSTALL=0
for arg in "$@"; do
    case "$arg" in
        --onefile) ONEFILE=1 ;;
        --skip-tests) SKIP_TESTS=1 ;;
        --install) INSTALL=1 ;;
        *) echo "unknown option $arg"; exit 2 ;;
    esac
done

if [ ! -x .venv/bin/python ]; then
    bash scripts/setup_venv.sh --dev
else
    .venv/bin/python -m pip install -q -r requirements-dev.txt
fi
PY=.venv/bin/python
VERSION=$("$PY" -c "import sys; sys.path.insert(0, 'src'); import flash; print(flash.__version__)")
OS=$(uname -s | tr '[:upper:]' '[:lower:]'); ARCH=$(uname -m)
echo "==> Flash $VERSION"

if [ "$SKIP_TESTS" = 0 ]; then
    echo "==> Running tests"
    QT_QPA_PLATFORM=offscreen "$PY" -m unittest tests.test_flash_core
fi

echo "==> Building executable"
FLASH_ONEFILE=$ONEFILE "$PY" -m PyInstaller --clean --noconfirm flash.spec
if [ "$ONEFILE" = 1 ]; then EXE=dist/Flash; else EXE=dist/Flash/Flash; fi

echo "==> Smoke testing $EXE"
"$EXE" --run-tool esptool version

mkdir -p release
if [ "$ONEFILE" = 1 ]; then
    cp "$EXE" "release/Flash-$VERSION-$OS-$ARCH"
    chmod +x "release/Flash-$VERSION-$OS-$ARCH"
    echo "==> Done: release/Flash-$VERSION-$OS-$ARCH"
    exit 0
fi

# Tarball layout:  Flash-<v>/Flash/...  +  Flash-<v>/install.sh
STAGE="build/stage/Flash-$VERSION"
rm -rf build/stage && mkdir -p "$STAGE"
cp -a dist/Flash "$STAGE/Flash"
cp scripts/install_linux.sh "$STAGE/install.sh"
chmod +x "$STAGE/install.sh" "$STAGE/Flash/Flash"
tar -C build/stage -czf "release/Flash-$VERSION-$OS-$ARCH.tar.gz" "Flash-$VERSION"
echo "==> Done: release/Flash-$VERSION-$OS-$ARCH.tar.gz"
echo "    users install it with:  tar xzf Flash-$VERSION-$OS-$ARCH.tar.gz && bash Flash-$VERSION/install.sh"

if [ "$INSTALL" = 1 ]; then
    bash scripts/install_linux.sh
fi
