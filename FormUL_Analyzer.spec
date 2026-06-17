# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('views', 'views'), ('utils', 'utils'), ('constants.py', '.'), ('ui.py', '.'), ('callbacks.py', '.'), ('fault_detection.py', '.'), ('math_channels.py', '.'), ('config.yaml', '.')]
binaries = []
hiddenimports = ['asammdf', 'asammdf.blocks', 'asammdf.blocks.mdf_v3', 'asammdf.blocks.mdf_v4', 'plotly', 'plotly.graph_objects', 'dash', 'dash.dcc', 'dash.html', 'flask', 'pandas', 'numpy', 'yaml', 'webview', 'webview.platforms.winforms', 'clr']
tmp_ret = collect_all('webview')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='FormUL_Analyzer',
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
