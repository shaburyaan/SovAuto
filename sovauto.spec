# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules


block_cipher = None

hiddenimports = [
    'win32timezone',
    'pywinauto.controls.common_controls',
    'pywinauto.controls.hwndwrapper',
    'pywinauto.controls.uia_controls',
    'pywinauto.controls.win32_controls',
    'pywinauto.uia_defines',
    'comtypes.client',
    'comtypes.stream',
]
hiddenimports += collect_submodules('pynput')

a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('build/branding/sovauto-logo.png', '.'),
        ('build/branding/sovauto.ico', '.'),
        ('Sovrano Main Logo 1.png', '.'),
        ('build/version/version.txt', 'build/version'),
        ('src/storage/migrations/*.sql', 'storage/migrations'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SovAuto',
    icon='build/branding/sovauto.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SovAuto',
)
