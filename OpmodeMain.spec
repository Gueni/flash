# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['OpModeMain.py'],
             pathex=['C:\\Users\\0xHunter\\Desktop\\Workspace\\PFE\\MicroTool'],
             binaries=[('C:\\Users\\Quazer\\.virtualenv\\pyqt5-36\\Lib\\site-packages\\PyQt5\\sip.pyd', 'PyQt5'), ('C:\\Users\\Quazer\\.virtualenv\\pyqt5-36\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\styles\\qwindowsvistastyle.dll', 'PyQt5\\Qt\\plugins\\styles')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='OpModeMain',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
