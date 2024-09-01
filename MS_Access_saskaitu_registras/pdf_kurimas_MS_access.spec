# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Raminta\\PycharmProjects\\MS_Access_saskaitu_registras\\pdf_kurimas_MS_access.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Raminta\\PycharmProjects\\MS_Access_saskaitu_registras\\times_new_roman\\times.ttf', 'times_new_roman'), ('C:\\Users\\Raminta\\PycharmProjects\\MS_Access_saskaitu_registras\\times_new_roman\\timesbd.ttf', 'times_new_roman')],
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
    name='pdf_kurimas_MS_access',
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
    icon=['C:\\Users\\Raminta\\PycharmProjects\\MS_Access_saskaitu_registras\\invoice_icon.ico'],
)
