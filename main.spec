# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=['D:/4 WORKSPACE/flash'],
    binaries=[],
    datas=[
        # Files from Theme/icons
        ('D:/4 WORKSPACE/flash/Theme/icons/checkbox_light.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/chip.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/collapsev.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/connected.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/connection.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/debug.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/disconnected.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/espLogo.png.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/Excel.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/executefuse1.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/expandv.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/fuse.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/GREY-GEAR-LOADING.gif', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/logo-color.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/setting.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/Settings.ico', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/sync.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/icons/wrongcom.png', 'Theme/icons'),
        ('D:/4 WORKSPACE/flash/Theme/stylesheet.qss', 'Theme'),

        # Files from Dependecies
        ('D:/4 WORKSPACE/flash/Dependecies/espefuse.py', 'Dependecies'),
        ('D:/4 WORKSPACE/flash/Dependecies/espsecure.py', 'Dependecies'),
        ('D:/4 WORKSPACE/flash/Dependecies/esptool.py', 'Dependecies'),
        ('D:/4 WORKSPACE/flash/Dependecies/samples.db', 'Dependecies'),
        ('D:/4 WORKSPACE/flash/Dependecies/settings.ini', 'Dependecies'),
        ('D:/4 WORKSPACE/flash/Dependecies/settingsprogresswrite.ini', 'Dependecies')
    ],
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
    icon='D:/4 WORKSPACE/flash/Theme/icons/flash.ico',
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
