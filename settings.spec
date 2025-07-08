# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['settings.py'],
    pathex=[],
    binaries=[],
    datas=[('ddddocr', 'ddddocr'), ('util.py', '.'), ('NonBrowser.py', '.'), ('ding-dong.wav', '.'), ('maxbot_logo2_single.ppm', '.'), ('icon_play_1.gif', '.'), ('icon_copy_2.gif', '.'), ('icon_query_5.gif', '.'), ('icon_chrome_4.gif', '.'), ('config', 'config')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='settings',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
