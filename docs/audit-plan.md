# Code Audit Plan — coord_convert_gui

**Date:** 2026-09-25
**Status:** Phases 1–3 complete. Phases 1–2 committed (`3fc3366`, `2b9885b`; Phase 1 pushed, Phase 2 local); Phase 3 (threading + PyInstaller packaging) implemented and verified offscreen, pending commit.

## 1. Background & scope

A full code audit of the PySide6 coordinate-converter GUI was performed after the
PyQt6 → PySide6 migration and project flattening. The findings were grouped into
three phases ordered by risk and effort:

- **Phase 1 — Hygiene & quick wins:** security, dependency, and correctness fixes
  that can be made in-place with no structural change.
- **Phase 2 — Package restructure & layout rewrite:** move app code into a proper
  Python package and rework the main-window layout.
- **Phase 3 — Threading & packaging:** move long-running work off the GUI thread
  and make the distributable build/entry point functional.

## 2. Audit findings

| ID | Severity | Finding | Location |
|----|----------|---------|----------|
| S1 | High | Settings stored as a **pickle** file inside the app directory (`resources/coordsys.ini`), tracked in git. Pickling untrusted-format state is a security risk; per-user state pollutes the install tree. | `main.py`, `resources/coordsys.ini` |
| S2 | High | Stale `requirements.txt` pinned `PyGeodesy==22.6.22`, whose module name was `geodesy`; the installed module is `pygeodesy`. Anyone installing from that file gets a broken environment. | `requirements.txt` |
| S3 | Medium | User/exception text injected unescaped into message boxes rendered as HTML (file errors, WKT view, conversion-error preview, startup error). | `main.py` |
| C2 | High | Legacy `.xls` import broken: `xlrd` not a dependency, so pandas cannot open `.xls`. `.xlsx` worked via openpyxl. | `pyproject.toml`, `_open_file` in `main.py` |
| C3 | Medium | File conversion overwrote the input lat/lon columns with formatted DMS strings in place, destroying the original data before output was written. | `_convert_file` in `main.py` |
| C4 | Low | Options dialog reverse-parsed the linear format string (`lin_fmt`) by slicing characters to recover precision/thousands-separator — fragile and lossy. | `options.py` |
| C5 | Low | `_add_column` named new columns `Column{len(columns)}`, which collides with existing names (e.g. after deleting a middle column). | `main.py` |
| C6 | Low | Non-string spreadsheet headers (e.g. numeric first row) broke combos, auto-detection and lookups that assume str labels. | `_open_file` in `main.py` |
| P1 | Medium | The out-of-bounds CRS check resolved a fresh `CRS` object for every entry of the ~5,600-row CRS database on **every** call — seconds of redundant work per conversion. | `_outside_crs_bounds` in `main.py` |
| A7 | Low | Dead relative-import fallback (`try: from . import ...`) left over from the pre-flatten package layout. | `main.py` |

Known edge case deferred during Phase 1, **resolved in Phase 2** (`2b9885b`):
in the bounds-warning suggestion loop, candidate CRSs were filtered by the
**target** CRS type even when the **source** CRS was the violator; suggestions
are now filtered by the violating CRS's own type.

## 3. Plan changes (vs. original audit proposal)

1. **`.xls`/`.xlsx` import pulled into Phase 1.** Originally a candidate for a
   later phase; at the user's request it was scoped into Phase 1 so spreadsheet
   import is fully functional now (add `xlrd`, verify both formats end-to-end).
2. **`requirements.txt` deleted, not regenerated.** The original plan allowed
   regenerating it from the lockfile; since uv (`pyproject.toml` + `uv.lock`) is
   the single source of truth, the stale file was removed outright.
3. **Settings fix expanded.** Beyond "stop using pickle", Phase 1 now includes:
   JSON format, a per-user config location (out of the app tree), validation and
   merging against defaults on load, plus a one-off *manual* migration of the
   existing pickle settings into the new JSON file (migration script run by hand;
   no pickle code shipped in the app).
4. **Phase 1 scope held to hygiene/quick-wins only.** Package restructure, layout
   rewrite, and threading were explicitly excluded and remain Phases 2–3.
5. **`resources/` stays at the repo root (Phase 2).** It is resolved from the
   package's parent directory instead of being moved into the package;
   bundling resources into a distributable wheel remains Phase 3 packaging work.
6. **Options dialog converted to layouts too (Phase 2).** The layout rewrite
   covered `options.py` (fixed-geometry construction) in addition to
   `mainwindow.ui`.
7. **Smoke test moved into the repo (Phase 2).** It now lives at
   `tests/smoke_test.py` (previously a throwaway `/tmp` script) and was
   extended with source-side bounds-suggestion coverage and `.xls`/`.xlsx`
   import through the app's `_open_file` path (file dialog stubbed; the
   `.xls` fixture needs optional `xlwt`, run via `uv run --with xlwt`).
8. **Explicit build-system added (Phase 2).** uv delegates editable installs to
   setuptools here, whose flat-layout auto-discovery fails with multiple
   top-level directories; `pyproject.toml` now pins `setuptools` and sets
   `packages.find include = ["coord_convert_gui*"]`.

## 4. Phase 1 — Hygiene & quick wins ✅ (commit `3fc3366`)

Steps (all completed):

1. **S1** Replace pickle load/save with JSON at a per-user config path
   (`~/Library/Application Support/coord_convert_gui/settings.json` on macOS;
   `%APPDATA%` on Windows; `$XDG_CONFIG_HOME` on Linux). Validate each loaded key
   against `_DEFAULT_SETTINGS` by type; merge over defaults. Untrack and
   gitignore `resources/coordsys.ini`.
2. **S2** Delete `requirements.txt`; keep uv/pyproject/lock as the dependency source of truth.
3. **C2** Add `xlrd>=2.0.1` to `pyproject.toml`; `uv sync` (lock updated, xlrd 2.0.2 installed).
   Verify `.xls` and `.xlsx` both read through the app's exact `pd.read_excel()` path
   using generated fixtures (`.xls` fixture written with throwaway `xlwt`, not a project dep).
4. **S3** `html.escape()` all dynamic text passed to message boxes.
5. **C3** Stop writing DMS strings back into the input columns during file conversion.
6. **C4** Replace `lin_fmt` string with `lin_prec` (int) + `lin_commas` (bool) settings;
   add `linear_format()` builder used by both single-point and file conversion.
7. **C5** `_add_column` skips colliding names.
8. **C6** Coerce column headers to str on load (`rename(columns=str)`).
9. **P1** Cache CRS name/area-of-use lookups with `functools.lru_cache`
   (`_crs_area()`); rewrite `_outside_crs_bounds` to consume the cached tuples.
10. **A7** Remove the dead relative-import fallback in `main.py`.

## 5. Phase 2 — Package restructure & layout rewrite ✅ (commit `2b9885b`)

Steps (all completed):

1. **Package move.** `main.py`, `options.py`, `ui_mainwindow.py` moved into
   `coord_convert_gui/` via `git mv` (history preserved) with an empty
   `__init__.py`; imports switched to relative (`from . import options`,
   `from .ui_mainwindow import Ui_MainWindow`).
2. **Packaging.** Entry point is now `coord_convert_gui.main:main`;
   `[tool.uv] package = true` makes uv install the project itself, so the old
   "project is not packaged" warning is gone and `uv run coord-convert` works.
   Explicit setuptools build config with
   `packages.find include = ["coord_convert_gui*"]` because flat-layout
   auto-discovery fails on `data/`, `icons/`, `resources/`.
3. **Resource paths.** `main.py` and `options.py` resolve `resources/` from
   the package's parent directory (repo root), independent of CWD;
   `resources/` was not moved (bundling into a wheel is Phase 3).
4. **UI regeneration.** New `scripts/regen_ui.py` runs `pyside6-uic` from the
   active environment and writes `coord_convert_gui/ui_mainwindow.py`; the
   regenerated file was verified to define every widget name the code uses.
5. **Layout rewrite.** `resources/mainwindow.ui` rebuilt around real Qt
   layouts (grid/box + spacers, 1062 → 462 lines): the window is now resizable
   with a proper minimum size (no more Fixed/Fixed policy); interactive tab =
   input panel | convert buttons | output panel; point-file tab = file row +
   expanding table above a bottom row of the two CRS group boxes flanking the
   action buttons. All widget object names, menus and actions preserved (only
   the anonymous `layoutWidget*` containers disappeared). The
   `_reflow_point_file_tab` resize hack in `main.py` was deleted;
   `OptionsDialog` was also converted from fixed geometry to layouts.
6. **Bounds-suggestion edge case.** Candidate CRSs are now filtered by the
   *violator's* type (`crs_type`) instead of always the target type, so a
   source-side violation suggests alternative source CRSs (e.g. a different
   UTM zone) rather than geographic ones. Covered by smoke-test step 8.
7. **Verification.** Smoke test moved to `tests/smoke_test.py` and extended
   (source-side suggestions; `.xls`/`.xlsx` import through `_open_file` with a
   stubbed file dialog). Full run passes offscreen, including both spreadsheet
   formats (`uv run --with xlwt python tests/smoke_test.py`). Entry-point
   launch verified offscreen.

Note carried to Phase 3 review: suggestion *ordering* still ranks candidates by
distance from their area-of-use bbox centre, so a global grid CRS (e.g.
EASE-Grid) can outrank the geographically closest UTM zone; all suggestions
are now at least of the correct CRS type.

## 6. Phase 3 — Threading & packaging ✅ (pending commit)

Steps (all completed):

1. **File conversion off the GUI thread.** A `_ConvertWorker` (`QThread`) in
   `main.py` runs the per-row transform loop on a worker thread. It receives a
   private copy of just the input columns plus the pyproj `Transformer`, format
   settings and CRS types, and writes its computed values into plain
   `results`/`errors` attributes. The main thread applies those results to the
   live model in `_on_convert_finished`, so pandas is only ever touched from the
   GUI thread. Single-point conversion stays synchronous (one transform).
2. **Progress + button state.** The worker emits a native-int `progress(done,
   total)` signal that updates the status bar with a running count/percentage;
   `_set_file_actions_enabled(False)` disables the point-file action buttons
   (`fileSelect`, `save_file`, `add_column`, `convert_file`) while a job runs and
   re-enables them on completion. A `closeEvent` override waits (bounded) for a
   running worker before the window closes.
3. **Per-row errors surfaced off-thread.** The worker collects per-row errors
   without blocking; `_on_convert_finished` shows the same "Conversion Errors"
   preview box as before once the job completes.
4. **PyInstaller packaging.** `coord-convert.spec` (one-dir, `--windowed`,
   `console=False`) bundles `crs.db`, `custom.css` and the icons under a top-level
   `resources/` dir via `datas=`, with a thin absolute-import launcher
   (`coord_convert_app.py`) as the entry point and `openpyxl`/`xlrd` listed as
   hiddenimports (pandas loads them lazily). Build: `uv run pyinstaller
   --noconfirm coord-convert.spec --distpath target` → `target/coord-convert.app`
   on macOS (a proper app bundle; see post-build fix below), a plain one-dir
   bundle at `target/coord-convert/` elsewhere.
5. **Frozen-aware resources.** New `coord_convert_gui/_resources.py` exposes
   `resource_dir()`: `<repo>/resources` in development, `sys._MEIPASS/resources`
   when frozen. Both `main.py` (`_RESOURCE_DIR`) and `options.py` now use it, so
   the packaged app finds its resources (verified: a one-dir `_MEIPASS` is the
   `_internal` dir where PyInstaller places bundled data).
6. **Verified on macOS.** The packaged binary launched offscreen reaches the Qt
   event loop with no missing-module/resource errors. The per-user settings path
   (`_settings_file()`) is already platform-aware (macOS `Application Support`,
   Windows `%APPDATA%`, Linux `$XDG_CONFIG_HOME`) and deliberately stays *outside*
   the bundle so runtime state never ships in the app tree.

Implementation notes:

- **Bounds check stays on the GUI thread.** It can raise a modal Yes/No dialog,
  which must run on the GUI thread; with Phase 1's `lru_cache`d `_crs_area()` it
  is fast after first use, so only the per-row loop (the genuinely long-running
  part) moved to the worker.
- **PySide6 queued-signal limitation.** A data-carrying signal of type
  `Signal(dict, list)` cannot be delivered across threads ("Cannot copy-convert
  dict to C++"); results are therefore plain attributes read after QThread's
  built-in no-arg `finished` signal fires, not passed as signal arguments.
- Smoke test gained step 10: threaded file conversion end-to-end (buttons disable
  mid-job, worker completes, results match a direct pyproj transform within 1 m,
  buttons re-enable), still passing offscreen.
- **Message-box text formats (post-build fix).** The Phase 1 S3 approach
  (`html.escape()` + `QMessageBox` AutoText) displayed literal `&quot;` entities
  in the WKT view: escaped text contains no HTML *tags*, so Qt's AutoText
  heuristic rendered it as plain text. Message boxes now set an explicit format
  -- `Qt.TextFormat.PlainText` for all dynamic content (WKT, file/conversion
  errors, startup error, bounds warning), `RichText` only for the static About
  dialog -- and the `html.escape()` calls were removed entirely (no HTML
  interpretation is possible for plain text). Covered by smoke-test step 11.
- **macOS `.app` bundle (post-build fix).** The first build produced a bare
  Mach-O executable at `target/coord-convert/coord-convert`; double-clicking it
  in Finder made macOS launch it through Terminal.app, so a terminal window
  appeared before the GUI. The spec now ends with a macOS-guarded `BUNDLE(...)`
  step (icon: generated `resources/Icon.icns`, display name "Coordinate
  Converter"), producing `target/coord-convert.app`. In that layout
  `sys._MEIPASS` is `Contents/Frameworks`, so the existing `resource_dir()`
  (`_MEIPASS/resources`) works unchanged (verified with a frozen probe bundle).
  The spec also removes the bare one-dir copy COLLECT leaves next to the `.app`,
  so the bundle is the only launchable artifact. Offscreen launch of
  `Contents/MacOS/coord-convert` reaches the event loop cleanly.

## 7. Verification approach

- **Offscreen smoke test** (`tests/smoke_test.py`, `QT_QPA_PLATFORM=offscreen`),
  covering: CRS DB load, main-window build from generated UI (all widget names
  present), real conversion cross-checked against an independent pyproj
  transform (1 m tolerance), reverse round-trip, TableModel data/setData/
  headerData, options dialog, out-of-bounds guard with target- *and*
  source-side suggestions, and spreadsheet import for both `.xls` and `.xlsx`
  through the app's `_open_file` path.
- **Entry point:** `uv run coord-convert` launches the app (verified offscreen;
  process stays alive in the Qt event loop).
- **Dependency check:** `uv sync` clean; `xlrd`/`openpyxl` importable in the venv.
- **Hygiene checks:** no stale references (`pickle`, old settings path, old module
  paths); `__pycache__` artifacts cleaned from the repo tree.
- **Git hygiene:** runtime state (settings) never tracked; `.gitignore` covers
  build output and per-user files.
