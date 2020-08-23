import sys
from PyQt5.QtWidgets import (QStatusBar, QMainWindow, QApplication, QMessageBox, 
                             QFileDialog, QDialog, QVBoxLayout, QRadioButton)
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
import sqlite3
from pyproj import Transformer, CRS
from pygeodesy.dms import parseDMS, latDMS, lonDMS
import pickle
import pandas as pd
import re
import csv
import options

Qt = QtCore.Qt
QIcon = QtGui.QIcon

crsObject = {}
qt_creator_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)

# create dictionary of settings to be saved


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


def get_crs_type(major, crs_name):
    return crsObject[major][crs_name][1]


# # get values from last session
with open('coordsys.ini', 'rb') as f:
    settings = pickle.load(f)
    if 'left_coord' not in settings:
        settings = {'left_coord': 'World',
                    'right_coord': 'World',
                    'left_crs': 'WGS 84',
                    'right_crs': 'WGS 84 / Zone 1N',
                    'ang_fmt': 'DMS',
                    'ang_prec': '2',
                    'lin_fmt': '{0:,.3f}'
                    }

loadCRS()

left_coord = settings['left_coord']
left_crs = settings['left_crs']
right_coord = settings['right_coord']
right_crs = settings['right_crs']

left_crs_type = get_crs_type(left_coord, left_crs)
right_crs_type = get_crs_type(right_coord, right_crs)


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def flags(self, index):
        fl = super(self.__class__,self).flags(index)
        fl |= Qt.ItemIsEditable
        fl |= Qt.ItemIsSelectable
        fl |= Qt.ItemIsEnabled
        fl |= Qt.ItemIsDragEnabled
        fl |= Qt.ItemIsDropEnabled
        return fl

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            # if not re.match(r'^-?\d+(?:\.\d+)?$', str(value)) is None:
            #     return '{:,.2f}'.format(value)
            # # if index.column() == 2 or index.column() == 3:
            # #     return '{:,.2f}'.format(value)
            # else:
            return str(value)

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            row = index.row()
            col = index.column()
            self._data.iloc[row][col] = value
            self.dataChanged.emit(index, index, (Qt.DisplayRole, ))
            return True
        return False

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:

                return str(self._data.index[section])

class MainWindow(QMainWindow, Ui_MainWindow):
    model = None

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        self.setWindowIcon(QIcon('globe.png'))
        self.setStatusBar(QStatusBar(self))
        self.setupUi(self)
        self.data = pd.DataFrame()

        def show_about_dialog():
            text = "<center>" \
                    "<h1>Coordinate Converter</h1>" \
                    "&#8291;" \
                    "<img src=globe.jfif>" \
                    "<p>Version 1.0.0<br/>" \
                    "Copyright &copy; A. Beckett 2020" \
                    "</center> </p>"
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QIcon('globe.png'))
            msgBox.setText(text)
            msgBox.setWindowTitle('About Coordinate Converter')

            msgBox.exec()
            # QMessageBox.about(self, "About Coordinate Converter", text)
        def open_file():
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            path = QFileDialog.getOpenFileName(window, "Open File", "", "CSV Files (*.csv)", options=options)[0]
            if path:
                self.filename.setText(path)
                # global data
                self.data = pd.read_csv(path)

                model = TableModel(self.data)
                self.tableview.setModel(model)
                self.tableview.verticalHeader().setDefaultSectionSize(20)
                no_cols = model.columnCount(self.tableview.rootIndex())
                # global column_list
                column_list = ['']
                for i in range(no_cols):
                    column_list.append(self.tableview.model()._data.columns[i])
                # load column selection combos
                self.combo_lat.clear()
                self.combo_lon.clear()
                self.combo_northing.clear()
                self.combo_easting.clear()
                self.combo_lat.addItems(column_list)
                self.combo_lon.addItems(column_list)
                self.combo_northing.addItems(column_list)
                self.combo_easting.addItems(column_list)

        self.fileSelect.clicked.connect(open_file)


        def save_file():
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "","CSV Files (*.csv)", options=options)
            if fileName:
                self.data.to_csv(fileName, index=False)

        self.save_file.clicked.connect(save_file)

        def options_dialog(self):
            global settings
            # dialog = QDialog()
            # dialog.ui = Form()
            # dialog.ui.setupUi(dialog)
            dialog = options.OptionsDialog(settings)
            returnCode = dialog.exec_()
            # print('returncode: ', returnCode)
            settings = dialog.get_settings()
            # print(settings)
    

        self.action_Options.triggered.connect(options_dialog)

        #enable menu items
        self.action_Exit.triggered.connect(self.close)
        self.action_About.triggered.connect(show_about_dialog)


        # create crsObject containing all available countries and crs codes
        # loadCRS()

        # create sorted list of countries
        countries_list = []
        for major in crsObject:
            countries_list.append(major)
        countries_list.sort()
        # load the two country combo boxes.for the interactive tab
        # make them default to the values saved in coordsys.ini'
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

        # load the two country combo boxes.for the file conversion tab
        # make them default to the values saved in coordsys.ini'
        self.left_coord_sys_file.addItems(countries_list)
        index = self.left_coord_sys_file.findText(left_coord, Qt.MatchFixedString)

        self.left_coord_sys_file.setCurrentIndex(index)
        self.updateLeftCRS_file(left_coord)

        index = self.left_crs_select_file.findText(left_crs, Qt.MatchFixedString)
        self.left_crs_select_file.setCurrentIndex(index)

        self.right_coord_sys_file.addItems(countries_list)
        index = self.right_coord_sys_file.findText(right_coord, Qt.MatchFixedString)

        self.right_coord_sys_file.setCurrentIndex(index)
        self.updateRightCRS_file(right_coord)

        index = self.right_crs_select_file.findText(right_crs, Qt.MatchFixedString)
        self.right_crs_select_file.setCurrentIndex(index)
        # self.updateRightCRS(countries_list[0])

        # update crs combo boxes if country is changed
        self.left_coord_sys.currentTextChanged.connect(self.updateLeftCRS)
        self.right_coord_sys.currentTextChanged.connect(self.updateRightCRS)
        self.left_coord_sys_file.currentTextChanged.connect(self.updateLeftCRS_file)
        self.right_coord_sys_file.currentTextChanged.connect(self.updateRightCRS_file)
        # get crs type after crs is selected and update labels
        self.left_crs_select.currentTextChanged.connect(self.get_left_crs_type)
        self.right_crs_select.currentTextChanged.connect(self.get_right_crs_type)
        self.left_crs_select_file.currentTextChanged.connect(self.get_left_crs_type_file)
        self.right_crs_select_file.currentTextChanged.connect(self.get_right_crs_type_file)

        # Update the appropriate labels to reflect coordinate systems stored in ini file
        # print('class __init__:',left_crs_type, right_crs_type)
        self.get_left_crs_type(left_crs_type)
        self.get_right_crs_type(right_crs_type)
        self.get_left_crs_type_file(left_crs_type)
        self.get_right_crs_type_file(right_crs_type)

        # do the coordinate transform.  Inputs are Latitude, Longitude
        # Outputs are Northing, Easting. CRS's for transform from left
        # and right combo boxes.

        self.convert.clicked.connect(self.convertCoords)
        self.convert_file.clicked.connect(self.convertFile)

        def AddColumn():
            no_cols = len(self.data.columns)
            no_rows = len(self.data.index)
            new_col = []
            for i in range(no_rows):
                new_col.append(float('NaN'))
            self.data.insert(no_cols,"Column"+str(no_cols),new_col)
            self.combo_lat.addItem("Column"+str(no_cols))
            self.combo_lon.addItem("Column"+str(no_cols))
            self.combo_northing.addItem("Column"+str(no_cols))
            self.combo_easting.addItem("Column"+str(no_cols))

            model = TableModel(self.data)
            self.tableview.setModel(model)

        self.add_column.clicked.connect(AddColumn)

        def showWKT(crs):
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QIcon('globe.png'))

            crs = CRS.from_user_input(crs)
            wkt = crs.to_wkt(pretty=True)
            msgBox.setText(wkt)
            msgBox.setWindowTitle("Well Known Text for EPSG:" + str(crs)[-4:])

            msgBox.exec()

        def showLeftWKT():

            coord_system = self.left_coord_sys.currentText()
            crs_name = self.left_crs_select.currentText()
            crs = crsObject[coord_system][crs_name][0]

            showWKT(crs)


        def showRightWKT():

            coord_system = self.right_coord_sys.currentText()
            crs_name = self.right_crs_select.currentText()
            crs = crsObject[coord_system][crs_name][0]

            showWKT(crs)

        def showLeftWKT_file():

            coord_system = self.left_coord_sys_file.currentText()
            crs_name = self.left_crs_select_file.currentText()
            crs = crsObject[coord_system][crs_name][0]

            showWKT(crs)

        def showRightWKT_file():

            coord_system = self.right_coord_sys_file.currentText()
            crs_name = self.right_crs_select_file.currentText()
            crs = crsObject[coord_system][crs_name][0]

            showWKT(crs)

 
        self.lWkt.clicked.connect(showLeftWKT)
        self.rWkt.clicked.connect(showRightWKT)

        self.lWkt_file.clicked.connect(showLeftWKT_file)
        self.rWkt_file.clicked.connect(showRightWKT_file)

    def clearNorthEast(self):
        # clear values in lat/lon boxes and status bar
        self.northing.setText('')
        self.easting.setText('')
        self.statusBar().showMessage('')


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
        self.clearNorthEast()
        # create list of crs for selected country
        crs_list = []
        for crs in crsObject[text]:
            crs_list.append(crs)
        crs_list.sort()
        self.right_crs_select.addItems(crs_list)

    def updateLeftCRS_file(self, text):
        self.left_crs_select_file.clear()

        # create list of crs for selected country
        crs_list = []
        for crs in crsObject[text]:
            crs_list.append(crs)
        crs_list.sort()
        self.left_crs_select_file.addItems(crs_list)

    def updateRightCRS_file(self, text):
        self.right_crs_select_file.clear()
        self.clearNorthEast()
        # create list of crs for selected country
        crs_list = []
        for crs in crsObject[text]:
            crs_list.append(crs)
        crs_list.sort()
        self.right_crs_select_file.addItems(crs_list)

    def convertCoords(self):

        # clear old results
        self.clearNorthEast()

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

        # checkto see that inputs are valid...
        if crs_from_type == 'geographic':
            pass

        # # set up appropriate formats
        # if self.optDms.isChecked():
        dms_format = settings['ang_fmt']
        precision = settings['ang_prec']
        
        lin_format = settings['lin_fmt']

        # Display EPSG codes  for conversion in status bar
        self.statusBar().showMessage('Coordinate transform from EPSG ' + str(crs_from) + ' to EPSG ' + str(crs_to))

        # process left side of conversion
        if crs_from_type == 'geographic':
            # parse the latitude, longitude input boxes using pyGeodesy function
            # check the entered values to ensure they are valid
            try:
                lat = parseDMS(self.latitude.text())
                if lat > 90.0 or lat < -90.0:
                    self.statusBar().showMessage('Latitude must be between -90 and +90')
                    return
            except ValueError:
                self.statusBar().showMessage('Invalid latitude')
                return
            try:
                lon = parseDMS(self.longitude.text())
                if lon > 180.0 or lon < -180.0:
                    self.statusBar().showMessage('Longitude must be between -180 and +180')
                    return
            except ValueError:
                self.statusBar().showMessage('Invalid longitude')
                return
        else:  # crs type is 'projected' need to reverse northing and easting
            if self.latitude.text() == '' or self.longitude.text() == '':
                self.statusBar().showMessage('Northing and/or easting cannot be blank')
                return
            try:
                lat = float(self.latitude.text().replace(',', ''))
            except ValueError:
                self.statusBar().showMessage('Invalid northing')
                return
            try:
                lon = float(self.longitude.text().replace(',', ''))
            except ValueError:
                self.statusBar().showMessage('Invalid easting')
                return

        # Do the transformation
        try:
            trans = Transformer.from_crs(crs_from, crs_to)
            if crs_from_type == 'geographic':
                results = trans.transform(lat, lon, errcheck=True)
            else:
                results = trans.transform(lon, lat, errcheck=True)
        except:
            print('transform error')
            self.statusBar().showMessage('Invalid conversion')
            return

        # output results according to crs_type
        if crs_to_type == 'projected':
            north = lin_format.format(results[1])
            east = lin_format.format(results[0])
            self.northing.setText(north)
            self.easting.setText(east)
        else:
            self.northing.setText(latDMS(results[0], form=dms_format, prec=precision))
            self.easting.setText(lonDMS(results[1], form=dms_format, prec=precision))

        if crs_from_type == 'geographic':
            self.latitude.setText(latDMS(lat, form=dms_format, prec=precision))
            self.longitude.setText(lonDMS(lon, form=dms_format, prec=precision))
        else:
            north = lin_format.format(lat)
            east = lin_format.format(lon)
            self.latitude.setText(north)
            self.longitude.setText(east)

        # save coordinate system selections
        settings['left_coord'] = left_coord
        settings['left_crs'] = left_crs
        settings['right_coord'] = right_coord
        settings['right_crs'] = right_crs

        with open('coordsys.ini','wb') as f:
            pickle.dump(settings, f)

    def convertFile(self):

        coord_system = self.left_coord_sys_file.currentText()
        crs_name = self.left_crs_select_file.currentText()
        left_coord = coord_system
        left_crs = crs_name
        crs_from = crsObject[coord_system][crs_name][0]
        crs_from_type = crsObject[coord_system][crs_name][1]
        coord_system = self.right_coord_sys_file.currentText()
        crs_name = self.right_crs_select_file.currentText()
        right_coord = coord_system
        right_crs = crs_name
        crs_to = crsObject[coord_system][crs_name][0]
        crs_to_type = crsObject[coord_system][crs_name][1]

        dms_format = settings['ang_fmt']
        precision = settings['ang_prec']
        lin_format = settings['lin_fmt']
        

        # crs_from = 4326
        # crs_to = 3124
        trans = Transformer.from_crs(crs_from, crs_to)

        # iterate over model, get values of columns  0 and 1, calculate values for cols 3 and 4
        no_rows = self.tableview.model().rowCount(self.tableview.rootIndex())

        model = self.tableview.model()

        # get columns for data
        lat_col = self.combo_lat.currentText()
        lon_col = self.combo_lon.currentText()
        northing_col = self.combo_northing.currentText()
        easting_col = self.combo_easting.currentText()

        for row in self.data.index:
            if crs_from_type == 'geographic':
                lat = parseDMS(self.data.loc[row, lat_col])
                lon = parseDMS(self.data.loc[row,lon_col])
                # make input column formats reflect user seleccted format
                self.data.loc[row, lat_col] = latDMS(lat, form=dms_format, prec=precision)
                self.data.loc[row, lon_col] = latDMS(lon, form=dms_format, prec=precision)
            else:
                lon = self.data.loc[row,lat_col]
                lat = self.data.at[row,lon_col]
            results = trans.transform(lat, lon, errcheck=True)
            if crs_to_type == 'geographic':
                # set column data type to string
                self.data[northing_col] = self.data[northing_col].astype('str')
                self.data[easting_col] = self.data[easting_col].astype('str')
                lat_dms = latDMS(results[0], form=dms_format, prec=precision)
                lon_dms = latDMS(results[1], form=dms_format, prec=precision)

                self.data.loc[row, northing_col] = lat_dms
                self.data.loc[row, easting_col] = lon_dms

            else: 
                self.data.loc[row, northing_col] = lin_format.format(results[1])
                self.data.loc[row,easting_col] = lin_format.format(results[0])
        # reset the model to show the newly computed values
        model = TableModel(self.data)
        self.tableview.setModel(model)

        # save coordinate system selections
        settings['left_coord'] = left_coord
        settings['left_crs'] = left_crs
        settings['right_coord'] = right_coord
        settings['right_crs'] = right_crs

        with open('coordsys.ini','wb') as f:
            pickle.dump(settings, f)

    def get_left_crs_type(self, text):
        if text != 'projected' and text != 'geographic' and text != '':
            left_crs_type = crsObject[self.left_coord_sys.currentText()][text][1]
        else:
            left_crs_type = text
        
        if left_crs_type:
            if left_crs_type == 'geographic':
                self.lLat.setText('Latitude')
                self.lLon.setText('Longitude')
            else:
                self.lLat.setText('Northing')
                self.lLon.setText('Easting')

    def get_right_crs_type(self, text):

        self.clearNorthEast()
        if text != 'projected' and text != 'geographic' and text != '':
            right_crs_type = crsObject[self.right_coord_sys.currentText()][text][1]
        else:
            right_crs_type = text
        if text!= '':
            if right_crs_type == 'geographic':
                self.rLat.setText('Latitude')
                self.rLon.setText('Longitude')
            else:
                self.rLat.setText('Northing')
                self.rLon.setText('Easting')

    def get_left_crs_type_file(self, text):
        if text != 'projected' and text != 'geographic' and text != '':
            left_crs_type_file = crsObject[self.left_coord_sys_file.currentText()][text][1]
        else:
            left_crs_type_file = text
        if text != '':
            if left_crs_type_file == 'geographic':
                self.label_latitude.setText('Latitude')
                self.label_longitude.setText('Longitude')
            else:
                self.label_latitude.setText('Northing')
                self.label_longitude.setText('Easting')

    def get_right_crs_type_file(self, text):
        if text != 'projected' and text != 'geographic' and text != '':
            right_crs_type_file = crsObject[self.right_coord_sys_file.currentText()][text][1]
        else:
            right_crs_type_file = text
        if text != '':
            if right_crs_type_file == 'geographic':
                self.label_northing.setText('Latitude')
                self.label_easting.setText('Longitude')
            else:
                self.label_northing.setText('Northing')
                self.label_easting.setText('Easting')

app = QApplication(sys.argv)
qss = 'custom.css'
with open(qss, 'r') as f:
    app.setStyleSheet(f.read())

window = MainWindow()
window.show()
app.exec_()
