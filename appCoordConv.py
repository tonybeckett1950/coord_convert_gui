import pathlib
import pickle
import sqlite3
import sys

import pandas as pd
from PyQt6 import QtCore, uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QStyle,
    QWidget,
)
from pygeodesy.dms import latDMS, lonDMS, parseDMS
from pyproj import CRS, Transformer

import options

_CRS_DB: dict = {}
_UI_FILE = "mainwindow.ui"
Ui_MainWindow, _ = uic.loadUiType(_UI_FILE)

_DEFAULT_SETTINGS: dict = {
    "left_coord": "World",
    "right_coord": "World",
    "left_crs": "WGS 84",
    "right_crs": "WGS 84 / Zone 1N",
    "ang_fmt": "DMS",
    "ang_prec": 2,
    "lin_fmt": "{0:,.3f}",
}

# Keywords used to auto-detect which file column maps to which coordinate field.
# Each key matches a combo-box field; values are lowercase aliases checked in order.
_FIELD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "lat":      ("lat", "latitude", "y", "lat_dd", "y_coord", "y_wgs84"),
    "lon":      ("lon", "long", "longitude", "x", "lon_dd", "x_coord", "x_wgs84"),
    "northing": ("northing", "north", "n", "y_out", "northing_out"),
    "easting":  ("easting", "east", "e", "x_out", "easting_out"),
}


def load_crs() -> dict:
    with sqlite3.connect("crs.db") as conn:
        rows = conn.execute(
            "SELECT country, crs_name, EPSG_code, crs_type FROM crs"
        ).fetchall()
    crs_db: dict = {}
    for country, crs_name, epsg_code, crs_type in rows:
        crs_db.setdefault(country, {})[crs_name] = [epsg_code, crs_type]
    return crs_db


def load_settings() -> dict:
    try:
        with open("coordsys.ini", "rb") as f:
            saved = pickle.load(f)
        if "left_coord" in saved:
            return saved
    except (FileNotFoundError, pickle.UnpicklingError):
        pass
    return _DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    try:
        with open("coordsys.ini", "wb") as f:
            pickle.dump(settings, f)
    except OSError:
        pass  # Settings are non-critical; silently skip if the file is unwritable


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data: pd.DataFrame) -> None:
        super().__init__()
        self._data = data

    def flags(self, index):
        return (
            super().flags(index)
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
        )

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignRight
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False
        self._data.iloc[index.row(), index.column()] = value
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
        return True

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        return self._data.shape[0]

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:
        return self._data.shape[1]

    def headerData(
        self, section, orientation, role=Qt.ItemDataRole.DisplayRole
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return str(self._data.columns[section])
        return str(self._data.index[section])


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, settings: dict) -> None:
        super().__init__()
        self.settings = settings
        self.data = pd.DataFrame()
        self._tab_auto_open_done = False
        self._opening_file = False
        self.setWindowIcon(QIcon("globe.png"))
        self.setStatusBar(QStatusBar(self))
        self.setupUi(self)
        self._setup_combos()
        self._connect_signals()
        QtCore.QTimer.singleShot(0, self._reflow_point_file_tab)

    # ── resize handling ──────────────────────────────────────────────────────

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        QtCore.QTimer.singleShot(0, self._reflow_point_file_tab)

    def _reflow_point_file_tab(self) -> None:
        """Keep CRS group boxes anchored to the bottom; expand the file display."""
        tab_h = self.point_file.height()
        if tab_h < 200:
            return
        # Original layout constants
        GB_HEIGHT = 200          # group box height (fixed)
        BOTTOM_GAP = 30          # gap below group boxes
        FILE_Y = 20              # top of file display
        FILE_GAP = 15            # gap between file display and group boxes
        gb_top = max(200, tab_h - BOTTOM_GAP - GB_HEIGHT)
        file_h = max(80, gb_top - FILE_GAP - FILE_Y)
        # Resize file display
        fdw = self.point_file.findChild(QWidget, 'file_display_widget')
        if fdw is not None:
            fdw.setGeometry(10, FILE_Y, 991, file_h)
        # Anchor group boxes to bottom
        self.groupBox_10.move(580, gb_top)
        self.groupBox_11.move(10, gb_top)
        # Keep buttons aligned with group boxes
        self.add_column.move(460, gb_top - 10)
        self.convert_file.move(460, gb_top + 50)
        self.save_file.move(460, gb_top + 85)

    # ── setup ────────────────────────────────────────────────────────────────

    def _setup_combos(self) -> None:
        countries = sorted(_CRS_DB)
        left_coord = self.settings.get("left_coord", _DEFAULT_SETTINGS["left_coord"])
        left_crs = self.settings.get("left_crs", _DEFAULT_SETTINGS["left_crs"])
        right_coord = self.settings.get("right_coord", _DEFAULT_SETTINGS["right_coord"])
        right_crs = self.settings.get("right_crs", _DEFAULT_SETTINGS["right_crs"])
        # Fall back to defaults if saved settings reference a CRS not in the DB
        if left_coord not in _CRS_DB or left_crs not in _CRS_DB.get(left_coord, {}):
            left_coord = _DEFAULT_SETTINGS["left_coord"]
            left_crs = _DEFAULT_SETTINGS["left_crs"]
        if right_coord not in _CRS_DB or right_crs not in _CRS_DB.get(right_coord, {}):
            right_coord = _DEFAULT_SETTINGS["right_coord"]
            right_crs = _DEFAULT_SETTINGS["right_crs"]
        self._init_combo_pair(
            self.left_coord_sys, self.left_crs_select,
            countries, left_coord, left_crs, self.updateLeftCRS,
        )
        self._init_combo_pair(
            self.right_coord_sys, self.right_crs_select,
            countries, right_coord, right_crs, self.updateRightCRS,
        )
        self._init_combo_pair(
            self.left_coord_sys_file, self.left_crs_select_file,
            countries, left_coord, left_crs, self.updateLeftCRS_file,
        )
        self._init_combo_pair(
            self.right_coord_sys_file, self.right_crs_select_file,
            countries, right_coord, right_crs, self.updateRightCRS_file,
        )
        left_type = _CRS_DB[left_coord][left_crs][1]
        right_type = _CRS_DB[right_coord][right_crs][1]
        self.get_left_crs_type(left_type)
        self.get_right_crs_type(right_type)
        self.get_left_crs_type_file(left_type)
        self.get_right_crs_type_file(right_type)

    def _init_combo_pair(
        self, country_combo, crs_combo, countries, country, crs, update_fn
    ) -> None:
        country_combo.addItems(countries)
        country_combo.setCurrentIndex(
            country_combo.findText(country, Qt.MatchFlag.MatchFixedString)
        )
        update_fn(country)
        crs_combo.setCurrentIndex(
            crs_combo.findText(crs, Qt.MatchFlag.MatchFixedString)
        )

    def _connect_signals(self) -> None:
        self.action_Exit.triggered.connect(self.close)
        self.action_About.triggered.connect(self._show_about)
        self.action_Options.triggered.connect(self._open_options)
        self.fileSelect.clicked.connect(self._open_file)
        self.save_file.clicked.connect(self._save_file)
        self.add_column.clicked.connect(self._add_column)
        self.convert.clicked.connect(self.convertCoords)
        self.convert_reverse.clicked.connect(self.convertCoordsReverse)
        self.convert_file.clicked.connect(self.convertFile)
        self.left_coord_sys.currentTextChanged.connect(self.updateLeftCRS)
        self.right_coord_sys.currentTextChanged.connect(self.updateRightCRS)
        self.left_coord_sys_file.currentTextChanged.connect(
            self.updateLeftCRS_file
        )
        self.right_coord_sys_file.currentTextChanged.connect(
            self.updateRightCRS_file
        )
        self.left_crs_select.currentTextChanged.connect(
            self.get_left_crs_type
        )
        self.right_crs_select.currentTextChanged.connect(
            self.get_right_crs_type
        )
        self.left_crs_select_file.currentTextChanged.connect(
            self.get_left_crs_type_file
        )
        self.right_crs_select_file.currentTextChanged.connect(
            self.get_right_crs_type_file
        )
        self.lWkt.clicked.connect(self._show_left_wkt)
        self.rWkt.clicked.connect(self._show_right_wkt)
        self.lWkt_file.clicked.connect(self._show_left_wkt_file)
        self.rWkt_file.clicked.connect(self._show_right_wkt_file)
        self.tabWidget.currentChanged.connect(self._on_tab_changed)

    # ── private helpers ──────────────────────────────────────────────────────

    def _message_box(self, title: str, text: str) -> None:
        msg = QMessageBox(self)
        msg.setWindowIcon(QIcon("globe.png"))
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()

    def _warning_yes_no(self, title: str, text: str) -> bool:
        """Warning dialog with a green-tick Yes and red-X No. Returns True if Yes."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(title)
        box.setText(text)
        _style = QApplication.style()
        yes_btn = box.addButton("  Yes", QMessageBox.ButtonRole.YesRole)
        yes_btn.setIcon(
            _style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        )
        no_btn = box.addButton("  No", QMessageBox.ButtonRole.NoRole)
        no_btn.setIcon(
            _style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
        )
        box.setDefaultButton(no_btn)
        box.exec()
        return box.clickedButton() is yes_btn

    def _sorted_crs_list(self, country: str) -> list:
        return sorted(_CRS_DB.get(country, {}))

    def _resolve_crs_type(self, text: str, country_combo) -> str:
        if text not in {"projected", "geographic", ""}:
            return _CRS_DB[country_combo.currentText()][text][1]
        return text

    def _set_coord_labels(
        self, crs_type: str, lat_widget, lon_widget
    ) -> None:
        if not crs_type:
            return
        if crs_type == "geographic":
            lat_widget.setText("Latitude")
            lon_widget.setText("Longitude")
        else:
            lat_widget.setText("Northing")
            lon_widget.setText("Easting")

    def _get_crs_selection(self, country_combo, crs_combo) -> tuple:
        country = country_combo.currentText()
        crs_name = crs_combo.currentText()
        if not country or not crs_name:
            raise ValueError("No CRS selected")
        entry = _CRS_DB.get(country, {}).get(crs_name)
        if entry is None:
            raise KeyError(f"CRS '{crs_name}' not found for '{country}'")
        return country, crs_name, entry[0], entry[1]

    def _persist_settings(
        self, left_coord, left_crs, right_coord, right_crs
    ) -> None:
        self.settings.update({
            "left_coord": left_coord,
            "left_crs": left_crs,
            "right_coord": right_coord,
            "right_crs": right_crs,
        })
        save_settings(self.settings)

    def _refresh_table(self) -> None:
        model = TableModel(self.data)
        self.tableview.setModel(model)
        self.tableview.verticalHeader().setDefaultSectionSize(20)
        self.tableview.resizeColumnsToContents()

    def _show_wkt(self, epsg_code) -> None:
        try:
            crs = CRS.from_user_input(epsg_code)
            self._message_box(
                f"Well Known Text for EPSG:{epsg_code}",
                crs.to_wkt(pretty=True),
            )
        except Exception as exc:
            self._message_box("Error", f"Cannot retrieve WKT:\n{exc}")

    # ── slots ────────────────────────────────────────────────────────────────

    def _show_about(self) -> None:
        self._message_box(
            "About Coordinate Converter",
            (
                "<center><h1>Coordinate Converter</h1>"
                "&#8291;<img src=globe.jfif>"
                "<p>Version 1.0.0<br/>"
                "Copyright &copy; A. Beckett 2020</p></center>"
            ),
        )

    def _on_tab_changed(self, index: int) -> None:
        """Open a file automatically the first time the Point File tab is shown."""
        if index == self.tabWidget.indexOf(self.point_file) and not self._tab_auto_open_done:
            self._tab_auto_open_done = True
            QtCore.QTimer.singleShot(0, self._open_file)

    def _auto_detect_columns(self) -> None:
        col_lower = {c.lower().strip(): c for c in self.data.columns}
        combo_map = {
            "lat":      self.combo_lat,
            "lon":      self.combo_lon,
            "northing": self.combo_northing,
            "easting":  self.combo_easting,
        }
        detected: list[str] = []
        undetected: list[str] = []
        for field, combo in combo_map.items():
            matched = next(
                (col_lower[kw] for kw in _FIELD_KEYWORDS[field] if kw in col_lower),
                None,
            )
            if matched:
                idx = combo.findText(matched, Qt.MatchFlag.MatchFixedString)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                    detected.append(f"{field} → \"{matched}\"")
                    continue
            undetected.append(field)
        parts: list[str] = []
        if detected:
            parts.append("Auto-detected: " + ", ".join(detected))
        if undetected:
            parts.append("Please map: " + ", ".join(undetected))
        if parts:
            self.statusBar().showMessage("  |  ".join(parts))

    def _open_file(self) -> None:
        if self._opening_file:
            return
        self._opening_file = True
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Spreadsheet Files (*.csv *.xls *.xlsx);;CSV Files (*.csv);;Excel Files (*.xls *.xlsx)",
        )
        QtCore.QTimer.singleShot(200, lambda: setattr(self, "_opening_file", False))
        if not path:
            return
        try:
            suffix = pathlib.Path(path).suffix.lower()
            self.data = (
                pd.read_excel(path)
                if suffix in (".xls", ".xlsx")
                else pd.read_csv(path)
            )
        except Exception as exc:
            self._message_box("File Error", f"Failed to open file:\n{exc}")
            return
        self.filename.setText(path)
        self._refresh_table()
        columns = [""] + list(self.data.columns)
        for combo in (
            self.combo_lat, self.combo_lon,
            self.combo_northing, self.combo_easting,
        ):
            combo.clear()
            combo.addItems(columns)
        self._auto_detect_columns()

    def _save_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx)",
        )
        if not path:
            return
        try:
            suffix = pathlib.Path(path).suffix.lower()
            if suffix == ".xlsx":
                self.data.to_excel(path, index=False)
            else:
                self.data.to_csv(path, index=False)
        except Exception as exc:
            self._message_box("File Error", f"Failed to save file:\n{exc}")

    def _open_options(self) -> None:
        dialog = options.OptionsDialog(self.settings)
        dialog.exec()
        self.settings = dialog.get_settings()

    def _add_column(self) -> None:
        col_name = f"Column{len(self.data.columns)}"
        self.data[col_name] = float("nan")
        for combo in (
            self.combo_lat, self.combo_lon,
            self.combo_northing, self.combo_easting,
        ):
            combo.addItem(col_name)
        self._refresh_table()

    def _show_left_wkt(self) -> None:
        try:
            epsg = _CRS_DB[self.left_coord_sys.currentText()][
                self.left_crs_select.currentText()
            ][0]
        except KeyError:
            return
        self._show_wkt(epsg)

    def _show_right_wkt(self) -> None:
        try:
            epsg = _CRS_DB[self.right_coord_sys.currentText()][
                self.right_crs_select.currentText()
            ][0]
        except KeyError:
            return
        self._show_wkt(epsg)

    def _show_left_wkt_file(self) -> None:
        try:
            epsg = _CRS_DB[self.left_coord_sys_file.currentText()][
                self.left_crs_select_file.currentText()
            ][0]
        except KeyError:
            return
        self._show_wkt(epsg)

    def _show_right_wkt_file(self) -> None:
        try:
            epsg = _CRS_DB[self.right_coord_sys_file.currentText()][
                self.right_crs_select_file.currentText()
            ][0]
        except KeyError:
            return
        self._show_wkt(epsg)

    # ── CRS combo updates ────────────────────────────────────────────────────

    def clearNorthEast(self) -> None:
        self.northing.setText("")
        self.easting.setText("")
        self.statusBar().showMessage("")

    def updateLeftCRS(self, text: str) -> None:
        if not text:
            return
        self.left_crs_select.clear()
        self.left_crs_select.addItems(self._sorted_crs_list(text))

    def updateRightCRS(self, text: str) -> None:
        if not text:
            return
        self.right_crs_select.clear()
        self.clearNorthEast()
        self.right_crs_select.addItems(self._sorted_crs_list(text))

    def updateLeftCRS_file(self, text: str) -> None:
        if not text:
            return
        self.left_crs_select_file.clear()
        self.left_crs_select_file.addItems(self._sorted_crs_list(text))

    def updateRightCRS_file(self, text: str) -> None:
        if not text:
            return
        self.right_crs_select_file.clear()
        self.clearNorthEast()
        self.right_crs_select_file.addItems(self._sorted_crs_list(text))

    def get_left_crs_type(self, text: str) -> None:
        self._set_coord_labels(
            self._resolve_crs_type(text, self.left_coord_sys),
            self.lLat, self.lLon,
        )

    def get_right_crs_type(self, text: str) -> None:
        self.clearNorthEast()
        self._set_coord_labels(
            self._resolve_crs_type(text, self.right_coord_sys),
            self.rLat, self.rLon,
        )

    def get_left_crs_type_file(self, text: str) -> None:
        self._set_coord_labels(
            self._resolve_crs_type(text, self.left_coord_sys_file),
            self.label_latitude, self.label_longitude,
        )

    def get_right_crs_type_file(self, text: str) -> None:
        self._set_coord_labels(
            self._resolve_crs_type(text, self.right_coord_sys_file),
            self.label_northing, self.label_easting,
        )

    # ── coordinate conversion ────────────────────────────────────────────────

    def _outside_crs_bounds(
        self,
        crs_from,
        crs_to,
        crs_from_type: str,
        crs_to_type: str,
        lat: float,
        lon: float,
    ) -> list[dict]:
        """Return info dicts for each CRS whose valid extent doesn't contain the point.

        Each dict has: label, epsg, crs_type, aou_name, south, north, west, east,
        lat_ok, lon_ok, geo_lat, geo_lon, suggestions.
        """
        if crs_from_type == "geographic":
            geo_lat, geo_lon = lat, lon
        else:
            try:
                to_geo = Transformer.from_crs(crs_from, 4326, always_xy=True)
                geo_lon, geo_lat = to_geo.transform(lon, lat)
            except Exception:
                return []

        def _in_bounds(aou) -> tuple[bool, bool]:
            lat_ok = aou.south <= geo_lat <= aou.north
            if aou.west <= aou.east:
                lon_ok = aou.west <= geo_lon <= aou.east
            else:
                lon_ok = geo_lon >= aou.west or geo_lon <= aou.east
            return lat_ok, lon_ok

        outside: list[dict] = []
        for epsg, label, crs_type in (
            (crs_from, "source", crs_from_type),
            (crs_to, "target", crs_to_type),
        ):
            try:
                crs_obj = CRS.from_user_input(epsg)
                aou = crs_obj.area_of_use
                if aou is None:
                    continue
                lat_ok, lon_ok = _in_bounds(aou)
                if lat_ok and lon_ok:
                    continue
                # Derive the datum/family prefix for prioritisation
                # e.g. "WGS 84" from "WGS 84 / UTM zone 31N"
                _full_name = crs_obj.name
                _family = _full_name.split(" / ")[0].strip()
                # Search _CRS_DB: bucket into same-family (priority) and others
                _priority: list[tuple[float, str]] = []  # (dist_to_point, label)
                _other: list[str] = []
                for country, entries in _CRS_DB.items():
                    for crs_name, (s_epsg, s_type) in entries.items():
                        if s_type != crs_to_type:
                            continue
                        try:
                            s_crs = CRS.from_user_input(s_epsg)
                            s_aou = s_crs.area_of_use
                            if s_aou is None:
                                continue
                            s_lat_ok, s_lon_ok = _in_bounds(s_aou)
                            if s_lat_ok and s_lon_ok:
                                entry_str = (
                                    f"{crs_name} \u2014 {country} (EPSG:{s_epsg})"
                                )
                                if _family and s_crs.name.startswith(_family):
                                    # Sort same-family by distance from bbox
                                    # centre to the input point so the most
                                    # geographically relevant zone comes first.
                                    c_lat = (s_aou.south + s_aou.north) / 2
                                    if s_aou.west <= s_aou.east:
                                        c_lon = (s_aou.west + s_aou.east) / 2
                                    else:  # crosses antimeridian
                                        c_lon = (s_aou.west + s_aou.east + 360) / 2
                                        if c_lon > 180:
                                            c_lon -= 360
                                    dist = (
                                        (c_lat - geo_lat) ** 2
                                        + (c_lon - geo_lon) ** 2
                                    ) ** 0.5
                                    _priority.append((dist, entry_str))
                                elif len(_other) < 5:
                                    _other.append(entry_str)
                        except Exception:
                            pass
                _priority.sort(key=lambda x: x[0])
                suggestions = [s for _, s in _priority[:5]] + _other
                suggestions = suggestions[:5]
                outside.append({
                    "label": label,
                    "epsg": epsg,
                    "crs_type": crs_type,
                    "aou_name": aou.name,
                    "south": aou.south,
                    "north": aou.north,
                    "west": aou.west,
                    "east": aou.east,
                    "lat_ok": lat_ok,
                    "lon_ok": lon_ok,
                    "geo_lat": geo_lat,
                    "geo_lon": geo_lon,
                    "suggestions": suggestions,
                })
            except Exception:
                pass
        return outside

    def _format_bounds_warning(self, violations: list[dict]) -> str:
        """Build a detailed warning message from _outside_crs_bounds results."""
        def _dd(deg: float, pos: str, neg: str) -> str:
            return f"{abs(deg):.4f}\u00b0{pos if deg >= 0 else neg}"

        sections: list[str] = []
        for info in violations:
            which: list[str] = []
            if not info["lat_ok"]:
                which.append(
                    f"Latitude {_dd(info['geo_lat'], 'N', 'S')} is outside "
                    f"{_dd(info['south'], 'N', 'S')}\u2013{_dd(info['north'], 'N', 'S')}"
                )
            if not info["lon_ok"]:
                which.append(
                    f"Longitude {_dd(info['geo_lon'], 'E', 'W')} is outside "
                    f"{_dd(info['west'], 'E', 'W')}\u2013{_dd(info['east'], 'E', 'W')}"
                )
            block = (
                f"{info['label'].capitalize()} CRS \"{info['aou_name']}\" "
                f"(EPSG:{info['epsg']}):\n"
                + "\n".join(f"  \u2022 {w}" for w in which)
            )
            if info["suggestions"]:
                block += f"\n  Suggested {info['label']} CRS for this location:"
                block += "\n" + "\n".join(
                    f"    \u2013 {s}" for s in info["suggestions"]
                )
            sections.append(block)
        return (
            "Coordinates fall outside the valid area:\n\n"
            + "\n\n".join(sections)
            + "\n\nConversion result may be inaccurate. Proceed?"
        )

    def convertCoords(self) -> None:
        self._convert_interactive(reverse=False)

    def convertCoordsReverse(self) -> None:
        self._convert_interactive(reverse=True)

    def _convert_interactive(self, reverse: bool) -> None:
        try:
            left_coord, left_crs, left_epsg, left_type = self._get_crs_selection(
                self.left_coord_sys, self.left_crs_select
            )
            right_coord, right_crs, right_epsg, right_type = self._get_crs_selection(
                self.right_coord_sys, self.right_crs_select
            )
        except (KeyError, ValueError):
            self.statusBar().showMessage("Please select a valid CRS for both sides")
            return
        if reverse:
            crs_from, crs_from_type = right_epsg, right_type
            crs_to, crs_to_type = left_epsg, left_type
            in_lat, in_lon = self.northing, self.easting
            out_lat, out_lon = self.latitude, self.longitude
            self.latitude.setText("")
            self.longitude.setText("")
        else:
            crs_from, crs_from_type = left_epsg, left_type
            crs_to, crs_to_type = right_epsg, right_type
            in_lat, in_lon = self.latitude, self.longitude
            out_lat, out_lon = self.northing, self.easting
            self.clearNorthEast()
        dms_format = self.settings["ang_fmt"]
        precision = self.settings["ang_prec"]
        lin_format = self.settings["lin_fmt"]
        self.statusBar().showMessage(
            f"Coordinate transform from EPSG {crs_from} to EPSG {crs_to}"
        )
        if crs_from_type == "geographic":
            try:
                lat = parseDMS(in_lat.text())
                if not -90.0 <= lat <= 90.0:
                    self.statusBar().showMessage(
                        "Latitude must be between -90 and +90"
                    )
                    return
            except ValueError:
                self.statusBar().showMessage("Invalid latitude")
                return
            try:
                lon = parseDMS(in_lon.text())
                if not -180.0 <= lon <= 180.0:
                    self.statusBar().showMessage(
                        "Longitude must be between -180 and +180"
                    )
                    return
            except ValueError:
                self.statusBar().showMessage("Invalid longitude")
                return
        else:
            if not in_lat.text() or not in_lon.text():
                self.statusBar().showMessage(
                    "Northing and/or easting cannot be blank"
                )
                return
            try:
                lat = float(in_lat.text().replace(",", ""))
            except ValueError:
                self.statusBar().showMessage("Invalid northing")
                return
            try:
                lon = float(in_lon.text().replace(",", ""))
            except ValueError:
                self.statusBar().showMessage("Invalid easting")
                return
        outside = self._outside_crs_bounds(
            crs_from, crs_to, crs_from_type, crs_to_type, lat, lon
        )
        if outside:
            if not self._warning_yes_no(
                "Outside Valid Area", self._format_bounds_warning(outside)
            ):
                return
        try:
            trans = Transformer.from_crs(crs_from, crs_to)
            args = (lat, lon) if crs_from_type == "geographic" else (lon, lat)
            results = trans.transform(*args, errcheck=True)
            if crs_to_type == "projected":
                out_lat.setText(lin_format.format(results[1]))
                out_lon.setText(lin_format.format(results[0]))
            else:
                out_lat.setText(latDMS(results[0], form=dms_format, prec=precision))
                out_lon.setText(lonDMS(results[1], form=dms_format, prec=precision))
            if crs_from_type == "geographic":
                in_lat.setText(latDMS(lat, form=dms_format, prec=precision))
                in_lon.setText(lonDMS(lon, form=dms_format, prec=precision))
            else:
                in_lat.setText(lin_format.format(lat))
                in_lon.setText(lin_format.format(lon))
        except Exception:
            self.statusBar().showMessage("Invalid conversion")
            return
        self._persist_settings(left_coord, left_crs, right_coord, right_crs)

    def convertFile(self) -> None:
        try:
            left_coord, left_crs, crs_from, crs_from_type = (
                self._get_crs_selection(
                    self.left_coord_sys_file, self.left_crs_select_file
                )
            )
            right_coord, right_crs, crs_to, crs_to_type = (
                self._get_crs_selection(
                    self.right_coord_sys_file, self.right_crs_select_file
                )
            )
        except (KeyError, ValueError):
            self.statusBar().showMessage("Please select a valid CRS for both sides")
            return
        dms_format = self.settings["ang_fmt"]
        precision = self.settings["ang_prec"]
        lin_format = self.settings["lin_fmt"]
        try:
            trans = Transformer.from_crs(crs_from, crs_to)
        except Exception as exc:
            self.statusBar().showMessage(f"Cannot build transformer: {exc}")
            return
        lat_col = self.combo_lat.currentText()
        lon_col = self.combo_lon.currentText()
        northing_col = self.combo_northing.currentText()
        easting_col = self.combo_easting.currentText()
        if not lat_col or not lon_col:
            self.statusBar().showMessage(
                "Please select Input columns from the dropdowns"
            )
            return
        if not northing_col or not easting_col:
            self.statusBar().showMessage(
                "Please select Output columns from the dropdowns"
            )
            return
        self.data[northing_col] = self.data[northing_col].astype(object)
        self.data[easting_col] = self.data[easting_col].astype(object)
        self.data[lat_col] = self.data[lat_col].astype(object)
        self.data[lon_col] = self.data[lon_col].astype(object)

        # Bounds check using the first valid row before committing to the batch
        if not self.data.empty:
            first = self.data.index[0]
            try:
                if crs_from_type == "geographic":
                    _chk_lat = parseDMS(self.data.loc[first, lat_col])
                    _chk_lon = parseDMS(self.data.loc[first, lon_col])
                else:
                    _chk_lat = float(self.data.loc[first, lat_col])
                    _chk_lon = float(self.data.loc[first, lon_col])
                outside = self._outside_crs_bounds(
                    crs_from, crs_to, crs_from_type, crs_to_type,
                    _chk_lat, _chk_lon,
                )
                if outside:
                    if not self._warning_yes_no(
                        "Outside Valid Area", self._format_bounds_warning(outside)
                    ):
                        return
            except Exception:
                pass  # If sample parse fails, skip guard and let the loop handle errors

        errors: list[str] = []
        for row in self.data.index:
            try:
                if crs_from_type == "geographic":
                    lat = parseDMS(self.data.loc[row, lat_col])
                    lon = parseDMS(self.data.loc[row, lon_col])
                    self.data.loc[row, lat_col] = latDMS(
                        lat, form=dms_format, prec=precision
                    )
                    self.data.loc[row, lon_col] = lonDMS(
                        lon, form=dms_format, prec=precision
                    )
                else:
                    lon = self.data.loc[row, lat_col]
                    lat = self.data.loc[row, lon_col]
                results = trans.transform(lat, lon, errcheck=True)
                if crs_to_type == "geographic":
                    self.data.loc[row, northing_col] = latDMS(
                        results[0], form=dms_format, prec=precision
                    )
                    self.data.loc[row, easting_col] = lonDMS(
                        results[1], form=dms_format, prec=precision
                    )
                else:
                    self.data.loc[row, northing_col] = lin_format.format(results[1])
                    self.data.loc[row, easting_col] = lin_format.format(results[0])
            except Exception as exc:
                errors.append(f"Row {row + 1}: {exc}")
        self._refresh_table()
        if errors:
            preview = "\n".join(errors[:10])
            suffix = f"\n\u2026and {len(errors) - 10} more" if len(errors) > 10 else ""
            self._message_box(
                "Conversion Errors",
                f"{len(errors)} row(s) could not be converted:\n\n{preview}{suffix}",
            )
        self._persist_settings(left_coord, left_crs, right_coord, right_crs)


def main() -> None:
    global _CRS_DB
    app = QApplication(sys.argv)
    try:
        _CRS_DB = load_crs()
    except Exception as exc:
        QMessageBox.critical(None, "Startup Error", f"Cannot load CRS database:\n{exc}")
        sys.exit(1)
    settings = load_settings()
    try:
        with open("custom.css") as f:
            app.setStyleSheet(f.read())
    except OSError:
        pass  # Stylesheet is optional
    window = MainWindow(settings)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
