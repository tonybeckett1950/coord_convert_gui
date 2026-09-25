from ._resources import resource_dir

from PySide6 import QtGui
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
)


class OptionsDialog(QDialog):

    def __init__(self, settings: dict) -> None:
        super().__init__()
        self.settings = settings
        self.setWindowTitle("Display Formats")
        resources = resource_dir()
        self.setWindowIcon(QtGui.QIcon(str(resources / "globe.png")))
        self.resize(491, 257)
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)

        ang_box = QGroupBox("Angular Measurements Format")
        ang_grid = QGridLayout(ang_box)
        self.optD = QRadioButton("Degrees", ang_box)
        self.optDM = QRadioButton("Degrees minutes", ang_box)
        self.optDMS = QRadioButton("Degrees minutes seconds", ang_box)
        self.spinD = QSpinBox(ang_box)
        self.spinDM = QSpinBox(ang_box)
        self.spinDMS = QSpinBox(ang_box)
        for spin in (self.spinD, self.spinDM, self.spinDMS):
            spin.setMaximumWidth(60)
        ang_grid.addWidget(self.optD, 0, 0)
        ang_grid.addWidget(self.optDM, 1, 0)
        ang_grid.addWidget(self.optDMS, 2, 0)
        for row, spin in enumerate((self.spinD, self.spinDM, self.spinDMS)):
            ang_grid.addWidget(QLabel("Decimal places", ang_box), row, 1)
            ang_grid.addWidget(spin, row, 2)
        ang_grid.setColumnStretch(1, 1)
        outer.addWidget(ang_box)

        lin_box = QGroupBox("Linear Measurements Format")
        lin_grid = QGridLayout(lin_box)
        self.chkCommas = QCheckBox("Comma separators", lin_box)
        self.spinLength = QSpinBox(lin_box)
        self.spinLength.setMaximumWidth(60)
        lin_grid.addWidget(self.chkCommas, 0, 0)
        lin_grid.addWidget(QLabel("Decimal places", lin_box), 0, 1)
        lin_grid.addWidget(self.spinLength, 0, 2)
        lin_grid.setColumnStretch(1, 1)
        outer.addWidget(lin_box)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_row.addStretch(1)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        outer.addLayout(btn_row)

    def _load_settings(self) -> None:
        ang_fmt = self.settings["ang_fmt"]
        ang_prec = int(self.settings["ang_prec"])
        options_map = {
            "D": (self.optD, self.spinD, 6),
            "DM": (self.optDM, self.spinDM, 4),
            "DMS": (self.optDMS, self.spinDMS, 2),
        }
        for fmt, (btn, spin, default_prec) in options_map.items():
            btn.setChecked(ang_fmt == fmt)
            spin.setValue(ang_prec if ang_fmt == fmt else default_prec)
        self.spinLength.setValue(int(self.settings["lin_prec"]))
        self.chkCommas.setChecked(bool(self.settings["lin_commas"]))

    def accept(self) -> None:
        if self.optD.isChecked():
            self.settings["ang_fmt"] = "D"
            self.settings["ang_prec"] = self.spinD.value()
        elif self.optDM.isChecked():
            self.settings["ang_fmt"] = "DM"
            self.settings["ang_prec"] = self.spinDM.value()
        else:
            self.settings["ang_fmt"] = "DMS"
            self.settings["ang_prec"] = self.spinDMS.value()
        self.settings["lin_prec"] = self.spinLength.value()
        self.settings["lin_commas"] = self.chkCommas.isChecked()
        super().accept()

    def get_settings(self) -> dict:
        return self.settings
