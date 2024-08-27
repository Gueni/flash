# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# Collect data files from both directories
data_files_dir1 = collect_data_files('D:/4 WORKSPACE/flash/Dependecies')
data_files_dir2 = collect_data_files('D:/4 WORKSPACE/flash/Theme')

# Combine the lists
datas = data_files_dir1 + data_files_dir2

a = Analysis(
    ['main.py'],
    pathex=['D:/4 WORKSPACE/flash'],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='flash 2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    codesign_identity=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='flash 2.0',
)
