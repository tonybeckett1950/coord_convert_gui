# Coordinate Converter GUI

PySide6 desktop app for converting coordinates between coordinate reference
systems (CRSs), interactively or in bulk from CSV / Excel files.

## Repository layout

- `coord_convert_gui/` — application package (`main.py`, `options.py`, and the
  generated `ui_mainwindow.py`)
- `resources/` — `mainwindow.ui`, CRS database (`crs.db`), stylesheet, icons
- `scripts/regen_ui.py` — regenerate `ui_mainwindow.py` from the `.ui` file
- `tests/smoke_test.py` — offscreen smoke test
- `data/samples/` — sample CSV files for testing and demos

## Development setup

```bash
uv sync                 # create .venv and install dependencies
uv run coord-convert    # run the app
```

### Regenerating the UI

After editing `resources/mainwindow.ui`:

```bash
uv run python scripts/regen_ui.py
```

### Tests

```bash
uv run python tests/smoke_test.py            # offscreen smoke test
uv run --with xlwt python tests/smoke_test.py  # also covers legacy .xls import
```

### Building a distributable (PyInstaller)

`pyinstaller` is a dev dependency (`uv sync` installs it). From the repo root:

```bash
uv run pyinstaller --noconfirm coord-convert.spec --distpath target
```

On macOS this produces `target/coord-convert.app` — a proper application
bundle, so double-clicking it launches the GUI directly (a bare executable
would open Terminal.app first). On Windows/Linux the output is the plain
one-dir bundle at `target/coord-convert/`. The CRS database, stylesheet and
icons are bundled under `resources/` inside the app and resolved via
`sys._MEIPASS` (see `coord_convert_gui/_resources.py`).

## Settings

Settings are stored per user as JSON in the platform config directory:

- macOS: `~/Library/Application Support/coord_convert_gui/settings.json`
- Windows: `%APPDATA%/coord_convert_gui/settings.json`
- Linux: `$XDG_CONFIG_HOME/coord_convert_gui/settings.json` (or `~/.config/...`)

