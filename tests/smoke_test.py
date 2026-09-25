"""Offscreen smoke test for the coordinate converter GUI.

Run from the repository root:
    uv run python tests/smoke_test.py

To also exercise legacy .xls import (fixture generation needs xlwt):
    uv run --with xlwt python tests/smoke_test.py
"""
import faulthandler
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# If the test hangs (e.g. a modal dialog opens), dump the Python stack and exit
faulthandler.enable()
faulthandler.dump_traceback_later(120, exit=True)

import pandas as pd  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402
from pyproj import Transformer  # noqa: E402

from coord_convert_gui import main, options  # noqa: E402

app = QApplication(sys.argv)

# Back up settings file (conversion test persists settings)
_SETTINGS = str(main._settings_file())
_BACKUP = _SETTINGS + ".bak_test"
if os.path.exists(_SETTINGS):
    shutil.copy2(_SETTINGS, _BACKUP)

try:
    # 1. CRS database loads
    main._CRS_DB = main.load_crs()
    assert "World" in main._CRS_DB and "WGS 84" in main._CRS_DB["World"]
    print("1. CRS DB OK:", len(main._CRS_DB), "countries")

    # 2. MainWindow builds from generated PySide6 UI
    settings = main._DEFAULT_SETTINGS.copy()
    w = main.MainWindow(settings)
    w.show()
    app.processEvents()
    for name in (
        "point_file", "groupBox_10", "groupBox_11", "tableview", "tabWidget",
        "latitude", "longitude", "northing", "easting",
        "left_coord_sys", "left_crs_select", "right_coord_sys", "right_crs_select",
        "fileSelect", "save_file", "add_column", "convert", "convert_reverse",
        "convert_file", "action_Exit", "action_About", "action_Options",
        "left_coord_sys_file", "left_crs_select_file",
        "right_coord_sys_file", "right_crs_select_file",
        "combo_lat", "combo_lon", "combo_northing", "combo_easting",
        "filename", "lWkt", "rWkt", "lWkt_file", "rWkt_file",
        "file_display_widget",
    ):
        assert hasattr(w, name), f"missing widget: {name}"
    print("2. MainWindow OK:", repr(w.windowTitle()))

    # 3. Real conversion through the UI logic (London -> UTM Zone 30N, which contains it)
    w.left_coord_sys.setCurrentIndex(w.left_coord_sys.findText("World"))
    w.left_crs_select.setCurrentIndex(w.left_crs_select.findText("WGS 84"))
    w.right_coord_sys.setCurrentIndex(w.right_coord_sys.findText("World"))
    w.right_crs_select.setCurrentIndex(
        w.right_crs_select.findText("WGS 84 / UTM zone 30N")
    )
    w.latitude.setText("51.4779")
    w.longitude.setText("-0.0015")
    w.convertCoords()
    app.processEvents()
    n_text, e_text = w.northing.text(), w.easting.text()
    print("3. Converted: northing =", n_text, "| easting =", e_text)
    assert n_text and e_text, "conversion produced no output"

    # Cross-check against a direct pyproj transform (tolerance 1 m)
    t = Transformer.from_crs(4326, "epsg:32630", always_xy=True)
    exp_e, exp_n = t.transform(-0.0015, 51.4779)
    got_n = float(n_text.replace(",", ""))
    got_e = float(e_text.replace(",", ""))
    assert abs(got_n - exp_n) < 1.0 and abs(got_e - exp_e) < 1.0, (
        got_n, got_e, exp_n, exp_e,
    )
    print("   matches direct pyproj result within 1 m")

    # 4. Reverse conversion round-trips
    w.convertCoordsReverse()
    app.processEvents()
    assert w.latitude.text() and w.longitude.text(), "reverse conversion empty"
    print("4. Reverse OK:", repr(w.latitude.text()), repr(w.longitude.text()))

    # 5. TableModel data/setData/headerData
    df = pd.DataFrame({"lat": ["51.4779"], "lon": ["-0.0015"], "n": [0.0], "e": [0.0]})
    model = main.TableModel(df)
    assert model.rowCount() == 1 and model.columnCount() == 4
    assert model.data(model.index(0, 0)) == "51.4779"
    assert model.headerData(3, w.tableview.horizontalHeader().orientation()) == "e"
    assert model.setData(model.index(0, 2), 123.0) is True
    print("5. TableModel OK")

    # 6. Options dialog
    od = options.OptionsDialog(settings)
    app.processEvents()
    od.accept()
    assert od.get_settings()["ang_fmt"] == "DMS"
    print("6. OptionsDialog OK:", od.get_settings())

    # 7. Out-of-bounds guard: London is outside UTM zone 1N (180W-174W) -> must flag target CRS
    violations = w._outside_crs_bounds(4326, 32601, "geographic", "projected", 51.4779, -0.0015)
    flagged = {v["epsg"] for v in violations}
    assert 32601 in flagged and 4326 not in flagged, flagged
    msg = w._format_bounds_warning(violations)
    assert "outside the valid area" in msg.lower() or "Outside Valid Area" in msg
    print("7. Bounds guard OK (flags EPSG:", sorted(flagged), ")")
    # 8. Source-side violation: suggestions must match the *source* CRS type.
    #    London expressed in UTM zone 31N coordinates is outside that zone; the
    #    suggested replacements must be projected CRSs (e.g. zone 30N), not
    #    geographic ones.
    e31, n31 = Transformer.from_crs(4326, "epsg:32631", always_xy=True).transform(
        -0.0015, 51.4779
    )
    violations = w._outside_crs_bounds(32631, 4326, "projected", "geographic", n31, e31)
    flagged = {v["epsg"] for v in violations}
    assert 32631 in flagged and 4326 not in flagged, flagged
    src_violation = next(v for v in violations if v["epsg"] == 32631)
    assert any("UTM zone 30N" in s for s in src_violation["suggestions"]), (
        src_violation["suggestions"]
    )
    print("8. Source-side suggestions OK:", src_violation["suggestions"][:2])

    # 9. Spreadsheet import through the app's _open_file path
    tmpdir = Path(tempfile.mkdtemp(prefix="ccg_smoke_"))
    rows = {"Latitude": [51.4779, 48.8566], "Longitude": [-0.0015, 2.3522]}

    class _FakeFileDialog:
        path = None

        @staticmethod
        def getOpenFileName(*args, **kwargs):
            return (_FakeFileDialog.path, "")

    orig_dialog = main.QFileDialog
    main.QFileDialog = _FakeFileDialog
    try:
        # 9a. .xlsx (openpyxl is a project dependency)
        xlsx = tmpdir / "pts.xlsx"
        pd.DataFrame(rows).to_excel(xlsx, index=False)
        _FakeFileDialog.path = str(xlsx)
        w._open_file()
        app.processEvents()
        assert list(w.data.columns) == ["Latitude", "Longitude"], list(w.data.columns)
        assert abs(float(w.data.iloc[0]["Latitude"]) - 51.4779) < 1e-9
        assert w.combo_lat.currentText() == "Latitude"
        print("9a. XLSX import OK:", list(w.data.columns))

        # 9b. Legacy .xls (fixture generation needs xlwt; skip if unavailable)
        try:
            import xlwt
        except ImportError:
            print(
                "9b. XLS import SKIPPED "
                "(run with: uv run --with xlwt python tests/smoke_test.py)"
            )
        else:
            xls = tmpdir / "pts.xls"
            wb = xlwt.Workbook()
            ws = wb.add_sheet("Sheet1")
            for c, header in enumerate(rows):
                ws.write(0, c, header)
            for r, (lat, lon) in enumerate(
                zip(rows["Latitude"], rows["Longitude"]), start=1
            ):
                ws.write(r, 0, lat)
                ws.write(r, 1, lon)
            wb.save(str(xls))
            _FakeFileDialog.path = str(xls)
            w._opening_file = False  # bypass the 200 ms debounce from 9a
            w._open_file()
            app.processEvents()
            assert list(w.data.columns) == ["Latitude", "Longitude"], (
                list(w.data.columns)
            )
            assert abs(float(w.data.iloc[0]["Latitude"]) - 51.4779) < 1e-9
            print("9b. XLS import OK:", list(w.data.columns))
    finally:
        main.QFileDialog = orig_dialog
        shutil.rmtree(tmpdir, ignore_errors=True)

    print("ALL SMOKE TESTS PASSED")
finally:
    if os.path.exists(_BACKUP):
        shutil.move(_BACKUP, _SETTINGS)
        print("(settings file restored)")

