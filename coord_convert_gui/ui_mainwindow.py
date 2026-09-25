# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QTabWidget,
    QTableView, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1030, 560)
        MainWindow.setMinimumSize(QSize(980, 520))
        self.action_Open = QAction(MainWindow)
        self.action_Open.setObjectName(u"action_Open")
        self.action_Close = QAction(MainWindow)
        self.action_Close.setObjectName(u"action_Close")
        self.action_Print = QAction(MainWindow)
        self.action_Print.setObjectName(u"action_Print")
        self.action_Exit = QAction(MainWindow)
        self.action_Exit.setObjectName(u"action_Exit")
        self.action_About = QAction(MainWindow)
        self.action_About.setObjectName(u"action_About")
        self.action_Options = QAction(MainWindow)
        self.action_Options.setObjectName(u"action_Options")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.interactive = QWidget()
        self.interactive.setObjectName(u"interactive")
        self.gridLayout_interactive = QGridLayout(self.interactive)
        self.gridLayout_interactive.setObjectName(u"gridLayout_interactive")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_4 = QGroupBox(self.interactive)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_4 = QGridLayout(self.groupBox_4)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.lLat = QLabel(self.groupBox_4)
        self.lLat.setObjectName(u"lLat")
        self.lLat.setMinimumSize(QSize(90, 0))

        self.gridLayout_4.addWidget(self.lLat, 0, 0, 1, 1)

        self.latitude = QLineEdit(self.groupBox_4)
        self.latitude.setObjectName(u"latitude")
        self.latitude.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_4.addWidget(self.latitude, 0, 1, 1, 1)

        self.lLon = QLabel(self.groupBox_4)
        self.lLon.setObjectName(u"lLon")
        self.lLon.setMinimumSize(QSize(90, 0))

        self.gridLayout_4.addWidget(self.lLon, 1, 0, 1, 1)

        self.longitude = QLineEdit(self.groupBox_4)
        self.longitude.setObjectName(u"longitude")
        self.longitude.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_4.addWidget(self.longitude, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_4)

        self.groupBox_9 = QGroupBox(self.interactive)
        self.groupBox_9.setObjectName(u"groupBox_9")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_9.sizePolicy().hasHeightForWidth())
        self.groupBox_9.setSizePolicy(sizePolicy)
        self.gridLayout_3 = QGridLayout(self.groupBox_9)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_11 = QLabel(self.groupBox_9)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(90, 0))

        self.gridLayout_3.addWidget(self.label_11, 0, 0, 1, 1)

        self.left_coord_sys = QComboBox(self.groupBox_9)
        self.left_coord_sys.setObjectName(u"left_coord_sys")
        self.left_coord_sys.setMinimumSize(QSize(260, 0))

        self.gridLayout_3.addWidget(self.left_coord_sys, 0, 1, 1, 1)

        self.label_12 = QLabel(self.groupBox_9)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(90, 0))

        self.gridLayout_3.addWidget(self.label_12, 1, 0, 1, 1)

        self.left_crs_select = QComboBox(self.groupBox_9)
        self.left_crs_select.setObjectName(u"left_crs_select")
        self.left_crs_select.setMinimumSize(QSize(260, 0))

        self.gridLayout_3.addWidget(self.left_crs_select, 1, 1, 1, 1)

        self.lWkt = QPushButton(self.groupBox_9)
        self.lWkt.setObjectName(u"lWkt")
        self.lWkt.setMinimumSize(QSize(90, 26))
        self.lWkt.setMaximumSize(QSize(90, 26))
        self.lWkt.setStyleSheet(u"background-color: #729FCF; color: white;")

        self.gridLayout_3.addWidget(self.lWkt, 2, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_9)


        self.gridLayout_interactive.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.verticalLayout_buttons = QVBoxLayout()
        self.verticalLayout_buttons.setObjectName(u"verticalLayout_buttons")
        self.interactiveTopSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_buttons.addItem(self.interactiveTopSpacer)

        self.horizontalLayout_convert = QHBoxLayout()
        self.horizontalLayout_convert.setObjectName(u"horizontalLayout_convert")
        self.convertLeftSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_convert.addItem(self.convertLeftSpacer)

        self.convert = QPushButton(self.interactive)
        self.convert.setObjectName(u"convert")
        self.convert.setMinimumSize(QSize(90, 26))
        self.convert.setStyleSheet(u"background-color: #73D216;")

        self.horizontalLayout_convert.addWidget(self.convert)

        self.convertRightSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_convert.addItem(self.convertRightSpacer)


        self.verticalLayout_buttons.addLayout(self.horizontalLayout_convert)

        self.horizontalLayout_convert_reverse = QHBoxLayout()
        self.horizontalLayout_convert_reverse.setObjectName(u"horizontalLayout_convert_reverse")
        self.reverseLeftSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_convert_reverse.addItem(self.reverseLeftSpacer)

        self.convert_reverse = QPushButton(self.interactive)
        self.convert_reverse.setObjectName(u"convert_reverse")
        self.convert_reverse.setMinimumSize(QSize(90, 26))
        self.convert_reverse.setStyleSheet(u"background-color: #73D216;")

        self.horizontalLayout_convert_reverse.addWidget(self.convert_reverse)

        self.reverseRightSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_convert_reverse.addItem(self.reverseRightSpacer)


        self.verticalLayout_buttons.addLayout(self.horizontalLayout_convert_reverse)

        self.interactiveBottomSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_buttons.addItem(self.interactiveBottomSpacer)


        self.gridLayout_interactive.addLayout(self.verticalLayout_buttons, 0, 1, 1, 1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_3 = QGroupBox(self.interactive)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_2 = QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.rLat = QLabel(self.groupBox_3)
        self.rLat.setObjectName(u"rLat")
        self.rLat.setMinimumSize(QSize(90, 0))

        self.gridLayout_2.addWidget(self.rLat, 0, 0, 1, 1)

        self.northing = QLineEdit(self.groupBox_3)
        self.northing.setObjectName(u"northing")
        self.northing.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.northing, 0, 1, 1, 1)

        self.rLon = QLabel(self.groupBox_3)
        self.rLon.setObjectName(u"rLon")
        self.rLon.setMinimumSize(QSize(90, 0))

        self.gridLayout_2.addWidget(self.rLon, 1, 0, 1, 1)

        self.easting = QLineEdit(self.groupBox_3)
        self.easting.setObjectName(u"easting")
        self.easting.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.easting, 1, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.groupBox_8 = QGroupBox(self.interactive)
        self.groupBox_8.setObjectName(u"groupBox_8")
        sizePolicy.setHeightForWidth(self.groupBox_8.sizePolicy().hasHeightForWidth())
        self.groupBox_8.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.groupBox_8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_7 = QLabel(self.groupBox_8)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(90, 0))

        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)

        self.right_coord_sys = QComboBox(self.groupBox_8)
        self.right_coord_sys.setObjectName(u"right_coord_sys")
        self.right_coord_sys.setMinimumSize(QSize(260, 0))

        self.gridLayout.addWidget(self.right_coord_sys, 0, 1, 1, 1)

        self.label_8 = QLabel(self.groupBox_8)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(90, 0))

        self.gridLayout.addWidget(self.label_8, 1, 0, 1, 1)

        self.right_crs_select = QComboBox(self.groupBox_8)
        self.right_crs_select.setObjectName(u"right_crs_select")
        self.right_crs_select.setMinimumSize(QSize(260, 0))

        self.gridLayout.addWidget(self.right_crs_select, 1, 1, 1, 1)

        self.rWkt = QPushButton(self.groupBox_8)
        self.rWkt.setObjectName(u"rWkt")
        self.rWkt.setMinimumSize(QSize(90, 26))
        self.rWkt.setMaximumSize(QSize(90, 26))
        self.rWkt.setStyleSheet(u"background-color: #729FCF; color: white;")

        self.gridLayout.addWidget(self.rWkt, 2, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBox_8)


        self.gridLayout_interactive.addLayout(self.verticalLayout_2, 0, 2, 1, 1)

        self.tabWidget.addTab(self.interactive, "")
        self.point_file = QWidget()
        self.point_file.setObjectName(u"point_file")
        self.verticalLayout_pointfile = QVBoxLayout(self.point_file)
        self.verticalLayout_pointfile.setObjectName(u"verticalLayout_pointfile")
        self.file_display_widget = QWidget(self.point_file)
        self.file_display_widget.setObjectName(u"file_display_widget")
        sizePolicy.setHeightForWidth(self.file_display_widget.sizePolicy().hasHeightForWidth())
        self.file_display_widget.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.file_display_widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.file_display_widget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.filename = QLineEdit(self.file_display_widget)
        self.filename.setObjectName(u"filename")

        self.horizontalLayout_2.addWidget(self.filename)

        self.fileSelect = QPushButton(self.file_display_widget)
        self.fileSelect.setObjectName(u"fileSelect")
        self.fileSelect.setMinimumSize(QSize(90, 26))
        self.fileSelect.setStyleSheet(u"background-color: #e0e0e0;")

        self.horizontalLayout_2.addWidget(self.fileSelect)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.tableview = QTableView(self.file_display_widget)
        self.tableview.setObjectName(u"tableview")

        self.verticalLayout_3.addWidget(self.tableview)


        self.verticalLayout_pointfile.addWidget(self.file_display_widget)

        self.horizontalLayout_bottom = QHBoxLayout()
        self.horizontalLayout_bottom.setObjectName(u"horizontalLayout_bottom")
        self.groupBox_11 = QGroupBox(self.point_file)
        self.groupBox_11.setObjectName(u"groupBox_11")
        self.gridLayout_6 = QGridLayout(self.groupBox_11)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_13 = QLabel(self.groupBox_11)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMinimumSize(QSize(90, 0))

        self.gridLayout_6.addWidget(self.label_13, 0, 0, 1, 1)

        self.left_coord_sys_file = QComboBox(self.groupBox_11)
        self.left_coord_sys_file.setObjectName(u"left_coord_sys_file")
        self.left_coord_sys_file.setMinimumSize(QSize(260, 0))

        self.gridLayout_6.addWidget(self.left_coord_sys_file, 0, 1, 1, 1)

        self.label_14 = QLabel(self.groupBox_11)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setMinimumSize(QSize(90, 0))

        self.gridLayout_6.addWidget(self.label_14, 1, 0, 1, 1)

        self.left_crs_select_file = QComboBox(self.groupBox_11)
        self.left_crs_select_file.setObjectName(u"left_crs_select_file")
        self.left_crs_select_file.setMinimumSize(QSize(260, 0))

        self.gridLayout_6.addWidget(self.left_crs_select_file, 1, 1, 1, 1)

        self.label_latitude = QLabel(self.groupBox_11)
        self.label_latitude.setObjectName(u"label_latitude")

        self.gridLayout_6.addWidget(self.label_latitude, 2, 0, 1, 1)

        self.combo_lat = QComboBox(self.groupBox_11)
        self.combo_lat.setObjectName(u"combo_lat")

        self.gridLayout_6.addWidget(self.combo_lat, 2, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox_11)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_6.addWidget(self.label_2, 2, 2, 1, 1)

        self.label_longitude = QLabel(self.groupBox_11)
        self.label_longitude.setObjectName(u"label_longitude")

        self.gridLayout_6.addWidget(self.label_longitude, 3, 0, 1, 1)

        self.combo_lon = QComboBox(self.groupBox_11)
        self.combo_lon.setObjectName(u"combo_lon")

        self.gridLayout_6.addWidget(self.combo_lon, 3, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox_11)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_6.addWidget(self.label_3, 3, 2, 1, 1)

        self.lWkt_file = QPushButton(self.groupBox_11)
        self.lWkt_file.setObjectName(u"lWkt_file")
        self.lWkt_file.setMinimumSize(QSize(90, 26))
        self.lWkt_file.setMaximumSize(QSize(90, 26))
        self.lWkt_file.setStyleSheet(u"background-color: #729FCF; color: white;")

        self.gridLayout_6.addWidget(self.lWkt_file, 4, 1, 1, 1)


        self.horizontalLayout_bottom.addWidget(self.groupBox_11)

        self.verticalLayout_filebuttons = QVBoxLayout()
        self.verticalLayout_filebuttons.setObjectName(u"verticalLayout_filebuttons")
        self.add_column = QPushButton(self.point_file)
        self.add_column.setObjectName(u"add_column")
        self.add_column.setMinimumSize(QSize(90, 26))
        self.add_column.setStyleSheet(u"background-color: #e0e0e0;")

        self.verticalLayout_filebuttons.addWidget(self.add_column)

        self.fileButtonGapSpacer = QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_filebuttons.addItem(self.fileButtonGapSpacer)

        self.convert_file = QPushButton(self.point_file)
        self.convert_file.setObjectName(u"convert_file")
        self.convert_file.setMinimumSize(QSize(90, 26))
        self.convert_file.setStyleSheet(u"background-color: #73D216;")

        self.verticalLayout_filebuttons.addWidget(self.convert_file)

        self.save_file = QPushButton(self.point_file)
        self.save_file.setObjectName(u"save_file")
        self.save_file.setMinimumSize(QSize(90, 26))
        self.save_file.setStyleSheet(u"background-color: #73D216;")

        self.verticalLayout_filebuttons.addWidget(self.save_file)

        self.fileButtonsBottomSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_filebuttons.addItem(self.fileButtonsBottomSpacer)


        self.horizontalLayout_bottom.addLayout(self.verticalLayout_filebuttons)

        self.groupBox_10 = QGroupBox(self.point_file)
        self.groupBox_10.setObjectName(u"groupBox_10")
        self.gridLayout_5 = QGridLayout(self.groupBox_10)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_9 = QLabel(self.groupBox_10)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(90, 0))

        self.gridLayout_5.addWidget(self.label_9, 0, 0, 1, 1)

        self.right_coord_sys_file = QComboBox(self.groupBox_10)
        self.right_coord_sys_file.setObjectName(u"right_coord_sys_file")
        self.right_coord_sys_file.setMinimumSize(QSize(260, 0))

        self.gridLayout_5.addWidget(self.right_coord_sys_file, 0, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox_10)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(90, 0))

        self.gridLayout_5.addWidget(self.label_10, 1, 0, 1, 1)

        self.right_crs_select_file = QComboBox(self.groupBox_10)
        self.right_crs_select_file.setObjectName(u"right_crs_select_file")
        self.right_crs_select_file.setMinimumSize(QSize(260, 0))

        self.gridLayout_5.addWidget(self.right_crs_select_file, 1, 1, 1, 1)

        self.label_northing = QLabel(self.groupBox_10)
        self.label_northing.setObjectName(u"label_northing")

        self.gridLayout_5.addWidget(self.label_northing, 2, 0, 1, 1)

        self.combo_northing = QComboBox(self.groupBox_10)
        self.combo_northing.setObjectName(u"combo_northing")

        self.gridLayout_5.addWidget(self.combo_northing, 2, 1, 1, 1)

        self.label_4 = QLabel(self.groupBox_10)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_5.addWidget(self.label_4, 2, 2, 1, 1)

        self.label_easting = QLabel(self.groupBox_10)
        self.label_easting.setObjectName(u"label_easting")

        self.gridLayout_5.addWidget(self.label_easting, 3, 0, 1, 1)

        self.combo_easting = QComboBox(self.groupBox_10)
        self.combo_easting.setObjectName(u"combo_easting")

        self.gridLayout_5.addWidget(self.combo_easting, 3, 1, 1, 1)

        self.label_5 = QLabel(self.groupBox_10)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_5.addWidget(self.label_5, 3, 2, 1, 1)

        self.rWkt_file = QPushButton(self.groupBox_10)
        self.rWkt_file.setObjectName(u"rWkt_file")
        self.rWkt_file.setMinimumSize(QSize(90, 26))
        self.rWkt_file.setMaximumSize(QSize(90, 26))
        self.rWkt_file.setStyleSheet(u"background-color: #729FCF; color: white;")

        self.gridLayout_5.addWidget(self.rWkt_file, 4, 1, 1, 1)


        self.horizontalLayout_bottom.addWidget(self.groupBox_10)


        self.verticalLayout_pointfile.addLayout(self.horizontalLayout_bottom)

        self.tabWidget.addTab(self.point_file, "")

        self.mainLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1030, 22))
        self.menu_File = QMenu(self.menubar)
        self.menu_File.setObjectName(u"menu_File")
        self.menu_About = QMenu(self.menubar)
        self.menu_About.setObjectName(u"menu_About")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_About.menuAction())
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.action_Close)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Options)
        self.menu_File.addAction(self.action_Print)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Exit)
        self.menu_About.addAction(self.action_About)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Coordinate Converter", None))
        self.action_Open.setText(QCoreApplication.translate("MainWindow", u"&Open", None))
        self.action_Close.setText(QCoreApplication.translate("MainWindow", u"&Save", None))
        self.action_Print.setText(QCoreApplication.translate("MainWindow", u"&Print", None))
        self.action_Exit.setText(QCoreApplication.translate("MainWindow", u"&Exit", None))
        self.action_About.setText(QCoreApplication.translate("MainWindow", u"&About", None))
        self.action_Options.setText(QCoreApplication.translate("MainWindow", u"Options", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Input Coordinates", None))
        self.lLat.setText(QCoreApplication.translate("MainWindow", u"Latitude", None))
        self.lLon.setText(QCoreApplication.translate("MainWindow", u"Longitude", None))
        self.groupBox_9.setTitle(QCoreApplication.translate("MainWindow", u"Input Coordinate System", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Country/Region", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"CRS", None))
        self.lWkt.setText(QCoreApplication.translate("MainWindow", u"WKT", None))
        self.convert.setText(QCoreApplication.translate("MainWindow", u"Convert >", None))
        self.convert_reverse.setText(QCoreApplication.translate("MainWindow", u"< Convert", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Output Coordinates", None))
        self.rLat.setText(QCoreApplication.translate("MainWindow", u"Northing", None))
        self.rLon.setText(QCoreApplication.translate("MainWindow", u"Easting", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("MainWindow", u"Output Coordinate System", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Country/Region", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"CRS", None))
        self.rWkt.setText(QCoreApplication.translate("MainWindow", u"WKT", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.interactive), QCoreApplication.translate("MainWindow", u"Interactive", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Input File", None))
        self.fileSelect.setText(QCoreApplication.translate("MainWindow", u"Open File", None))
        self.groupBox_11.setTitle(QCoreApplication.translate("MainWindow", u"Input Coordinate System", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Country/Region", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"CRS", None))
        self.label_latitude.setText(QCoreApplication.translate("MainWindow", u"Latitude", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Choose column", None))
        self.label_longitude.setText(QCoreApplication.translate("MainWindow", u"Longitude", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Choose column", None))
        self.lWkt_file.setText(QCoreApplication.translate("MainWindow", u"WKT", None))
        self.add_column.setText(QCoreApplication.translate("MainWindow", u"Add Column", None))
        self.convert_file.setText(QCoreApplication.translate("MainWindow", u"Convert >", None))
        self.save_file.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.groupBox_10.setTitle(QCoreApplication.translate("MainWindow", u"Output Coordinate System", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Country/Region", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"CRS", None))
        self.label_northing.setText(QCoreApplication.translate("MainWindow", u"Northing", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Choose column", None))
        self.label_easting.setText(QCoreApplication.translate("MainWindow", u"Easting", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Choose column", None))
        self.rWkt_file.setText(QCoreApplication.translate("MainWindow", u"WKT", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.point_file), QCoreApplication.translate("MainWindow", u"Point File", None))
        self.menu_File.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menu_About.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
    # retranslateUi

