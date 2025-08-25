# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['JOGO DO PASSARO.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/', 'assets/'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JogoDoPassaro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # ⬅️ IMPORTANTE: DESATIVADO!
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=None,
)