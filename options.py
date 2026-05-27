from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class OptionsDialog(QDialog):

    def __init__(self, settings: dict) -> None:
        super().__init__()
        self.settings = settings
        self.setWindowTitle("Display Formats")
        self.setWindowIcon(QtGui.QIcon("globe.png"))
        self.resize(491, 257)
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        ang_box = QGroupBox("Angular Measurements Format", self)
        ang_box.setGeometry(QtCore.QRect(20, 10, 451, 131))

        layout_widget = QWidget(ang_box)
        layout_widget.setGeometry(QtCore.QRect(10, 30, 196, 83))
        layout = QVBoxLayout(layout_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.optD = QRadioButton("Degrees", layout_widget)
        self.optDM = QRadioButton("Degrees minutes", layout_widget)
        self.optDMS = QRadioButton("Degrees minutes seconds", layout_widget)
        for btn in (self.optD, self.optDM, self.optDMS):
            layout.addWidget(btn)

        self.spinD = QSpinBox(ang_box)
        self.spinD.setGeometry(QtCore.QRect(390, 30, 49, 26))
        self.spinDM = QSpinBox(ang_box)
        self.spinDM.setGeometry(QtCore.QRect(390, 60, 49, 26))
        self.spinDMS = QSpinBox(ang_box)
        self.spinDMS.setGeometry(QtCore.QRect(390, 90, 49, 26))

        for y in (30, 60, 90):
            QLabel("Decimal places", ang_box).setGeometry(
                QtCore.QRect(280, y, 101, 26)
            )

        lin_box = QGroupBox("Linear Measurements Format", self)
        lin_box.setGeometry(QtCore.QRect(20, 150, 451, 61))

        QLabel("Decimal places", lin_box).setGeometry(
            QtCore.QRect(280, 30, 101, 26)
        )
        self.spinLength = QSpinBox(lin_box)
        self.spinLength.setGeometry(QtCore.QRect(390, 30, 49, 26))
        self.chkCommas = QCheckBox("Comma separators", lin_box)
        self.chkCommas.setGeometry(QtCore.QRect(10, 30, 171, 23))

        btn_ok = QPushButton("OK", self)
        btn_ok.setGeometry(QtCore.QRect(310, 220, 83, 25))
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel", self)
        btn_cancel.setGeometry(QtCore.QRect(70, 220, 83, 25))
        btn_cancel.clicked.connect(self.reject)

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
        lin_prec = int(self.settings["lin_fmt"][-3:-2])
        self.spinLength.setValue(lin_prec)
        self.chkCommas.setChecked("," in self.settings["lin_fmt"])

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
        prec = self.spinLength.value()
        sep = ",." if self.chkCommas.isChecked() else "."
        self.settings["lin_fmt"] = f"{{0:{sep}{prec}f}}"
        super().accept()

    def get_settings(self) -> dict:
        return self.settings
