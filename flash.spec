#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?              __          _ __    __
#?             / /_  __  __(_) /___/ /
#?            / __ \/ / / / / / __  /
#?           / /_/ / /_/ / / / /_/ /
#?          /_.___/\__,_/_/_/\__,_/
#?
#?
#? Name:        flash.spec
#? Purpose:     PyInstaller build definition. Builds a one-folder app (dist/Flash) that the Inno Setup installer
#?              packages; set FLASH_ONEFILE=1 for a single portable executable instead.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
import  os
import  sys
from    pathlib                     import  Path

from    PyInstaller.utils.hooks     import  collect_data_files, collect_submodules
#?----------------------------------------------------------------------------------------------------------------------------------------
ROOT                        = Path(SPECPATH)
SRC                         = ROOT / "src"
sys.path.insert(0, str(SRC))
from    flash                       import  __version__                                # noqa: E402
#?----------------------------------------------------------------------------------------------------------------------------------------
ONEDIR                      = os.environ.get("FLASH_ONEFILE") != "1"
NAME                        = "Flash"

# esptool & friends load chip definitions, flasher stubs and eFuse tables at runtime.
tool_packages               = ["esptool", "espefuse", "espsecure", "esp_pylib"]
datas                       = [(str(SRC / "flash" / "assets"), "flash/assets")]
hiddenimports               = []
for pkg in tool_packages:
    datas                  += collect_data_files(pkg)
    hiddenimports          += collect_submodules(pkg)
hiddenimports              += collect_submodules("rich") + collect_submodules("rich_click")
hiddenimports              += collect_submodules("flash") + ["serial.tools.list_ports", "openpyxl"]

a                           = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "PyQt5", "PyQt6", "PySide2", "matplotlib", "numpy", "IPython", "pytest"],
    noarchive=False,
    optimize=0,
)
pyz                         = PYZ(a.pure)

icon                        = str(ROOT / "src" / "flash" / "assets" / "flash.ico") if sys.platform == "win32" else None
version                     = None
if sys.platform == "win32":                                                            # file properties shown by Explorer
    nums                    = tuple(int(x) for x in (__version__.split(".") + ["0", "0", "0"])[:4])
    version                 = str(ROOT / "build" / "version_info.txt")
    os.makedirs(os.path.dirname(version), exist_ok=True)
    Path(version).write_text(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={nums}, prodvers={nums}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'Mohamed Gueni'),
      StringStruct('FileDescription', 'Flash - ESP32 / ESP8266 flashing toolkit'),
      StringStruct('FileVersion', '{__version__}'),
      StringStruct('InternalName', '{NAME}'),
      StringStruct('OriginalFilename', '{NAME}.exe'),
      StringStruct('ProductName', '{NAME}'),
      StringStruct('ProductVersion', '{__version__}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""", encoding="utf-8")

if ONEDIR:
    exe                     = EXE(pyz, a.scripts, [], exclude_binaries=True, name=NAME, console=False, icon=icon,
                                  version=version, upx=False, debug=False, strip=False)
    coll                    = COLLECT(exe, a.binaries, a.datas, name=NAME, upx=False, strip=False)
else:
    exe                     = EXE(pyz, a.scripts, a.binaries, a.datas, [], name=NAME, console=False, icon=icon,
                                  version=version, upx=False, debug=False, strip=False, runtime_tmpdir=None)
#?----------------------------------------------------------------------------------------------------------------------------------------
