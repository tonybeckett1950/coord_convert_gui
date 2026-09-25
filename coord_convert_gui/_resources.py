"""Frozen-aware resource path resolution.

In development the resources live in ``<repo root>/resources`` (one level above
this package). When frozen with PyInstaller they are bundled into the app's data
directory -- ``sys._MEIPASS`` for a one-file build, the ``_internal`` directory
for a one-dir build -- and must be resolved from there instead of the source tree.
"""
import pathlib
import sys


def resource_dir() -> pathlib.Path:
    """Return the absolute path to this build's ``resources`` directory."""
    if getattr(sys, "frozen", False):  # running as a PyInstaller bundle
        meipass = getattr(sys, "_MEIPASS", None)
        base = (
            pathlib.Path(meipass)
            if meipass
            else pathlib.Path(sys.executable).resolve().parent
        )
    else:  # plain interpreter (development / tests)
        base = pathlib.Path(__file__).resolve().parent.parent
    return base / "resources"
