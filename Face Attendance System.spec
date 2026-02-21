# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('dataset', 'dataset'), ('database.db', '.'), ('/Users/nezeelsonani/Documents/GitHub/face-attendance-system/.venv311/lib/python3.11/site-packages/face_recognition_models', 'face_recognition_models')]
binaries = []
hiddenimports = ['cv2', 'face_recognition', 'face_recognition_models', 'dlib', 'matplotlib']
tmp_ret = collect_all('face_recognition_models')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['.'],
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
    [],
    exclude_binaries=True,
    name='Face Attendance System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Face Attendance System',
)
app = BUNDLE(
    coll,
    name='Face Attendance System.app',
    icon=None,
    bundle_identifier=None,
)
