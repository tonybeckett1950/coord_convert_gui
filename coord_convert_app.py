"""PyInstaller entry point for the Coordinate Converter GUI.

This thin launcher exists so PyInstaller can analyse a single top-level script
that uses *absolute* imports. The package's own ``main.py`` relies on relative
imports and therefore cannot be used directly as a bundle entry point.
"""
from coord_convert_gui.main import main

if __name__ == "__main__":
    main()
