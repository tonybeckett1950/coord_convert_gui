# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog


class OptionsDialog(QDialog):
    # global settings

    def __init__(self, settings):
        super(OptionsDialog, self).__init__()   
        
        self.settings = settings          

        self.setWindowTitle('Display Formats') 
        self.setWindowIcon(QtGui.QIcon('globe.png'))
        self.resize(491, 257)

        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setTitle("Angular Measurements Format")
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 451, 131))
        self.groupBox.setObjectName("groupBox")

        self.spinD = QtWidgets.QSpinBox(self.groupBox)
        self.spinD.setGeometry(QtCore.QRect(390, 30, 49, 26))
        self.spinD.setObjectName("spinD")

        self.spinDM = QtWidgets.QSpinBox(self.groupBox)
        self.spinDM.setGeometry(QtCore.QRect(390, 60, 49, 26))
        self.spinDM.setObjectName("spinDM")

        self.spinDMS = QtWidgets.QSpinBox(self.groupBox)
        self.spinDMS.setGeometry(QtCore.QRect(390, 90, 49, 26))
        self.spinDMS.setObjectName("spinDMS")

        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(280, 30, 101, 26))
        self.label.setObjectName("label")
        self.label.setText("Decimal places")

        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(280, 60, 101, 26))
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Decimal places")

        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(280, 90, 101, 26))
        self.label_3.setObjectName("label_3")
        self.label_3.setText("Decimal places")

        self.layoutWidget = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 30, 196, 83))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.optD = QtWidgets.QRadioButton(self.layoutWidget)
        self.optD.setChecked(True)
        self.optD.setObjectName("optD")
        self.optD.setText("Degrees")
        self.verticalLayout.addWidget(self.optD)

        self.optDM = QtWidgets.QRadioButton(self.layoutWidget)
        self.optDM.setObjectName("optDM")
        self.optDM.setText("Degrees minutes")
        self.verticalLayout.addWidget(self.optDM)
        self.optDMS = QtWidgets.QRadioButton(self.layoutWidget)

        self.optDMS.setObjectName("optDMS")
        self.optDMS.setText("Degrees minutes seconds")
        self.verticalLayout.addWidget(self.optDMS)

        if self.settings['ang_fmt'] == 'D':
            self.spinD.setProperty("value", settings['ang_prec'])
            self.optD.setChecked(True)
        else:
            self.spinD.setProperty("value", 6)
            self.optD.setChecked(False)
        
        if self.settings['ang_fmt'] == 'DM':
            self.spinDM.setProperty("value", settings['ang_prec'])
            self.optDM.setChecked(True)
        else:
            self.spinDM.setProperty("value", 4)
            self.optDM.setChecked(False)

        if self.settings['ang_fmt'] == 'DMS':
            self.spinDMS.setProperty("value", settings['ang_prec'])
            self.optDMS.setChecked(True)
        else:
            self.spinDMS.setProperty("value", 2)
            self.optDMS.setChecked(False)  

        self.groupBox_2 = QtWidgets.QGroupBox(self)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 150, 451, 61))
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("Linear Measurements Format")

        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(280, 30, 101, 26))
        self.label_4.setObjectName("label_4")
        self.label_4.setText("Decimal places")

        self.spinLength = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinLength.setGeometry(QtCore.QRect(390, 30, 49, 26))
        lin_prec = settings['lin_fmt'][-3:-2]
        self.spinLength.setProperty("value", int(lin_prec))
        self.spinLength.setObjectName("spinLength")

        self.chkCommas = QtWidgets.QCheckBox(self.groupBox_2)
        self.chkCommas.setGeometry(QtCore.QRect(10, 30, 171, 23))
        if ',' in settings['lin_fmt']:
            self.chkCommas.setChecked(True)
        else:
            self.chkCommas.setChecked(False)
        self.chkCommas.setObjectName("chkCommas")
        self.chkCommas.setText("Comma separators")

        self.pushButtonOK = QtWidgets.QPushButton(self)
        self.pushButtonOK.setGeometry(QtCore.QRect(310, 220, 83, 25))
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.pushButtonOK.setText('OK')

        self.pushButtonCancel = QtWidgets.QPushButton(self)
        self.pushButtonCancel.setGeometry(QtCore.QRect(70, 220, 83, 25))
        self.pushButtonCancel.setText('Cancel')
        self.pushButtonCancel.setObjectName("pushButtonCancel")

        self.pushButtonOK.clicked.connect(self.accept)
        self.pushButtonCancel.clicked.connect(lambda: self.close())
 

    def accept(self):
        # print('Exited options dialog with OK')
        if self.optD.isChecked():
            self.settings['ang_fmt'] = 'D'
            self.settings['ang_prec'] = self.spinD.value()
        elif self.optDM.isChecked():
            self.settings['ang_fmt'] = 'DM'
            self.settings['ang_prec'] = self.spinDM.value()
        else:
            self.settings['ang_fmt'] = 'DMS'
            self.settings['ang_prec'] = self.spinDMS.value()

        lin_prec = str(self.spinLength.value()) + 'f'
        if self.chkCommas.isChecked():
            self.settings['lin_fmt'] = '{0:,.' + lin_prec + '}'
        else:
            self.settings['lin_fmt'] = '{0:.' + lin_prec + '}'
        
        self.close()


    def get_settings(self):
        return self.settings

