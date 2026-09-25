#!/usr/bin/env python3
"""Regenerate coord_convert_gui/ui_mainwindow.py from resources/mainwindow.ui.

Usage (from the repository root):
    uv run python scripts/regen_ui.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _find_uic() -> str:
    """Locate the pyside6-uic executable of the active environment."""
    found = shutil.which("pyside6-uic")
    if found:
        return found
    fallback = Path(sys.prefix) / ("Scripts" if os.name == "nt" else "bin") / (
        "pyside6-uic.exe" if os.name == "nt" else "pyside6-uic"
    )
    if fallback.exists():
        return str(fallback)
    raise SystemExit("pyside6-uic not found; run this script via `uv run`")


def main() -> int:
    ui_file = ROOT / "resources" / "mainwindow.ui"
    out_file = ROOT / "coord_convert_gui" / "ui_mainwindow.py"
    result = subprocess.run([_find_uic(), str(ui_file), "-o", str(out_file)])
    if result.returncode == 0:
        print(f"regenerated {out_file.relative_to(ROOT)}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
