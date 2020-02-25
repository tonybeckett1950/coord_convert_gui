import sys
from PyQt5.QtWidgets import QStatusBar, QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5 import uic
import sqlite3
from pyproj import Transformer, CRS
from pygeodesy.dms import parseDMS, latDMS, lonDMS
import pickle

crsObject = {}
qt_creator_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)

# set default crs types
left_crs_type = 'geographic'
right_crs_type = 'projected'

# dms_format = 'dms'
# precision = 2

# get values from last session
with open('coordsys.ini', 'rb') as f:
    left_coord, left_crs, right_coord, right_crs = pickle.load(f)
print(left_coord, left_crs)
print(right_coord, right_crs)


def loadCRS():
    connection = sqlite3.connect('crs.db')
    cursor = connection.cursor()
    query = 'SELECT country, crs_name, EPSG_code, crs_type from crs'
    cursor.execute(query)
    sql_result = list(cursor)
    connection.close()

    for result in sql_result:
        major_area = result[0]
        crs_name = result[1]
        EPSG_code = result[2]
        crs_type = result[3]

        if major_area not in crsObject:
            crsObject[major_area] = {}

        if crs_name not in crsObject[major_area]:
            crsObject[major_area][crs_name] = [EPSG_code, crs_type]


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        self.setWindowIcon(QIcon('globe.png'))
        self.setStatusBar(QStatusBar(self))
        self.setupUi(self)

        # create crsObject containing all available countries and crs codes
        loadCRS()

        # create sorted list of countries
        countries_list = []
        for major in crsObject:
            countries_list.append(major)
        countries_list.sort()
        # load the two country combo boxes.
        # make the left boxes default to 'World' and 'WGS84'
        self.left_coord_sys.addItems(countries_list)
        index = self.left_coord_sys.findText(left_coord, Qt.MatchFixedString)

        self.left_coord_sys.setCurrentIndex(index)
        self.updateLeftCRS(left_coord)

        index = self.left_crs_select.findText(left_crs, Qt.MatchFixedString)
        self.left_crs_select.setCurrentIndex(index)

        self.right_coord_sys.addItems(countries_list)
        index = self.right_coord_sys.findText(right_coord, Qt.MatchFixedString)

        self.right_coord_sys.setCurrentIndex(index)
        self.updateRightCRS(right_coord)

        index = self.right_crs_select.findText(right_crs, Qt.MatchFixedString)
        self.right_crs_select.setCurrentIndex(index)
        # self.updateRightCRS(countries_list[0])

        # update crs combo boxes if country is changed
        self.left_coord_sys.currentTextChanged.connect(self.updateLeftCRS)
        self.right_coord_sys.currentTextChanged.connect(self.updateRightCRS)
        # get crs type after crs is selected and update labels
        self.left_crs_select.currentTextChanged.connect(self.get_left_crs_type)
        self.right_crs_select.currentTextChanged.connect(self.get_right_crs_type)

        # do the coordinate transform.  Inputs are Latitude, Longitude
        # Outputs are Northing, Easting. CRS's for transform from left
        # and right combo boxes.

        self.convert.clicked.connect(self.convertCoords)

        def showLeftWKT():

            coord_system = self.left_coord_sys.currentText()
            crs_name = self.left_crs_select.currentText()
            crs = crsObject[coord_system][crs_name][0]

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QIcon('globe.png'))

            crs = CRS.from_user_input(crs)
            wkt = crs.to_wkt(pretty=True)
            msgBox.setText(wkt)
            msgBox.setWindowTitle("Well Known Text for EPSG:" + str(crs)[-4:])

            msgBox.exec()

        def showRightWKT():

            coord_system = self.right_coord_sys.currentText()
            crs_name = self.right_crs_select.currentText()
            crs = crsObject[coord_system][crs_name][0]

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QIcon('globe.png'))

            crs = CRS.from_user_input(crs)
            wkt = crs.to_wkt(pretty=True)
            msgBox.setText(wkt)
            msgBox.setWindowTitle("Well Known Text for EPSG:" + str(crs)[-4:])

            msgBox.exec()

        self.lWkt.clicked.connect(showLeftWKT)
        self.rWkt.clicked.connect(showRightWKT)

    def updateLeftCRS(self, text):
        self.left_crs_select.clear()
        # create list of crs for selected country
        crs_list = []
        for crs in crsObject[text]:
            crs_list.append(crs)
        crs_list.sort()
        self.left_crs_select.addItems(crs_list)

    def updateRightCRS(self, text):
        self.right_crs_select.clear()
        # create list of crs for selected country
        crs_list = []
        for crs in crsObject[text]:
            crs_list.append(crs)
        crs_list.sort()
        self.right_crs_select.addItems(crs_list)

    def convertCoords(self):

        coord_system = self.left_coord_sys.currentText()
        crs_name = self.left_crs_select.currentText()
        left_coord = coord_system
        left_crs = crs_name
        crs_from = crsObject[coord_system][crs_name][0]
        crs_from_type = crsObject[coord_system][crs_name][1]
        coord_system = self.right_coord_sys.currentText()
        crs_name = self.right_crs_select.currentText()
        right_coord = coord_system
        right_crs = crs_name
        crs_to = crsObject[coord_system][crs_name][0]
        crs_to_type = crsObject[coord_system][crs_name][1]

        # set up appropriate formats
        if self.optDms.isChecked():
            dms_format = 'dms'
            precision = 2
        elif self.optDm.isChecked():
            dms_format = 'dm'
            precision = 4
        else:
            dms_format = 'd'
            precision = 6

        # Display EPSG codes  for conversion in status bar
        self.statusBar().showMessage('Coordinate transform from EPSG ' + str(crs_from) + ' to EPSG ' + str(crs_to))

        # process left side of conversion
        if crs_from_type == 'geographic':
            # parse the latitude, longitude input boxes using pyGeodesy function
            lat = parseDMS(self.latitude.text())
            lon = parseDMS(self.longitude.text())
        else:  # crs type is 'projected' need to reverse northing and easting
            lat = float(self.latitude.text())
            lon = float(self.longitude.text())

        # Do the transformation
        trans = Transformer.from_crs(crs_from, crs_to)
        if crs_from_type == 'geographic':
            results = trans.transform(lat, lon)
        else:
            results = trans.transform(lon, lat)

        # output results according to crs_type
        if crs_to_type == 'projected':
            north = "{0:,.2f}".format(results[1])
            east = "{0:,.2f}".format(results[0])
            self.northing.setText(north)
            self.easting.setText(east)
        else:
            self.northing.setText(latDMS(results[0], form=dms_format, prec=precision))
            self.easting.setText(lonDMS(results[1], form=dms_format, prec=precision))

        if crs_from_type == 'geographic':
            self.latitude.setText(latDMS(lat, form=dms_format, prec=precision))
            self.longitude.setText(lonDMS(lon, form=dms_format, prec=precision))
        else:
            north = "{0:,.2f}".format(lat)
            east = "{0:,.2f}".format(lon)
            self.latitude.setText(north)
            self.longitude.setText(east)

        # save coordinate system selections
        with open('coordsys.ini','wb') as f:
            pickle.dump([left_coord, left_crs, right_coord, right_crs], f)

    def get_left_crs_type(self, text):
        if text != '':
            left_crs_type = crsObject[self.left_coord_sys.currentText()][text][1]
            if left_crs_type == 'geographic':
                self.lLat.setText('Latitude')
                self.lLon.setText('Longitude')
            else:
                self.lLat.setText('Northing')
                self.lLon.setText('Easting')

    def get_right_crs_type(self, text):
        if text != '':
            right_crs_type = crsObject[self.right_coord_sys.currentText()][text][1]
            if right_crs_type == 'geographic':
                self.rLat.setText('Latitude')
                self.rLon.setText('Longitude')
            else:
                self.rLat.setText('Northing')
                self.rLon.setText('Easting')


app = QApplication(sys.argv)
qss = 'custom.css'
with open(qss, 'r') as f:
    app.setStyleSheet(f.read())

window = MainWindow()
window.show()
app.exec_()
