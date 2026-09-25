# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build definition for the Coordinate Converter GUI.

Produces a one-dir, windowed (no console) bundle named ``coord-convert``.
On macOS it is wrapped in a proper ``coord-convert.app`` bundle so Finder /
LaunchServices launch it directly -- a bare executable would open Terminal.app.
Build from the repository root:

    uv run pyinstaller --noconfirm coord-convert.spec --distpath target

Resources are bundled under a top-level ``resources/`` directory inside the
bundle so the frozen-aware ``resource_dir()`` (see
``coord_convert_gui/_resources.py``) finds them via ``sys._MEIPASS``.
"""
import os
import sys

# Files the app reads at runtime, each bundled into <bundle>/resources/.
_RESOURCE_FILES = [
    "crs.db",
    "custom.css",
    "globe.png",
    "globe.jfif",
    "Icon.ico",
]

datas = [
    (os.path.join(SPECPATH, "resources", name), "resources")
    for name in _RESOURCE_FILES
]

a = Analysis(
    [os.path.join(SPECPATH, "coord_convert_app.py")],
    pathex=[SPECPATH],
    binaries=[],
    datas=datas,
    # pandas imports these Excel engines lazily at runtime; PyInstaller's static
    # analysis cannot see them, so list them explicitly.
    hiddenimports=["openpyxl", "xlrd"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="coord-convert",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # --windowed: run without a console window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="coord-convert",
)

# On macOS, wrap the one-dir output in a real .app bundle. Without this, the
# dist contains a bare Mach-O executable, which Finder runs through
# Terminal.app (a terminal window appears before the GUI). BUNDLE is a
# macOS-only PyInstaller builder, so guard it for portability.
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="coord-convert.app",
        icon=os.path.join(SPECPATH, "resources", "Icon.icns"),
        bundle_version="1.0.0",
        info_plist={
            "CFBundleDisplayName": "Coordinate Converter",
            "CFBundleShortVersionString": "1.0.0",
        },
    )
    # COLLECT also leaves a bare one-dir copy next to the .app; remove it so
    # the bundle is the only launchable artifact (double-clicking the bare
    # executable would open Terminal.app again).
    import shutil as _shutil

    _bare = os.path.join(DISTPATH, "coord-convert")
    if os.path.isdir(_bare):
        _shutil.rmtree(_bare)
