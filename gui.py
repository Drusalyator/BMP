"""This file implements the graphical version of program"""
import sys
import logging
from core import *
from PyQt5 import QtWidgets
from PyQt5 import QtCore


class Window(QtWidgets.QMainWindow):
    """Main window"""

    def __init__(self, picture_name=None):
        super().__init__()
        self.picture_name = picture_name
        self._get_picture_structure(self.picture_name)
        self._init_window()

    def _init_window(self):
        """Initialize window"""
        self.setWindowTitle("BMP structure")
        self.showMaximized()

    def _get_picture_structure(self, picture_name):
        """Get information about picture"""
        if picture_name is None or picture_name == "":
            picture_name = QtWidgets.QFileDialog.getOpenFileName(self, "Load picture", filter="Data (*.bmp)")[0]
            self.picture_name = picture_name
        try:
            with open(self.picture_name, 'rb') as file:
                self.picture = open_picture(self.picture_name)
                self.picture_header = read_bitmap_file_header(self.picture)
                self.picture_info = select_info(self.picture, self.picture_header)
                if self.picture_info.bit_count <= 8:
                    self.color_table = get_color_table(self.picture, self.picture_info)
        except Exception as exception:
            QtWidgets.QMessageBox.warning(self, "Error", "Error: {}".format(exception), QtWidgets.QMessageBox.Ok)
            sys.exit("Incorrect picture")
        else:
            self.dock_widget = QtWidgets.QDockWidget(self)
            self.dock_widget.hide()
            table_info = TableInfo()
            table_info.fill_table_info(self.picture_header, self.picture_info)
            self.dock_widget.setWidget(table_info)
            self.dock_widget.show()

    def _center(self):
        """Set application on center"""
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


class TableInfo(QtWidgets.QWidget):
    """Table with information about picture"""

    def __init__(self, perent=None):
        """Initialize class"""
        super().__init__(perent)
        self._init_table()

    def _init_table(self):
        """Initialize widgets on a record table"""
        self.title_label = QtWidgets.QLabel("Picture Info", self)
        layout = QtWidgets.QVBoxLayout(self)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        self.table_info = QtWidgets.QTableWidget(self)
        self.table_info.setColumnCount(2)
        item = QtWidgets.QTableWidgetItem("Field")
        self.table_info.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem("Value")
        self.table_info.setHorizontalHeaderItem(1, item)
        self.table_info.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.title_label)
        layout.addWidget(self.table_info)
        self.setLayout(layout)
        self.show()

    def _add_info_in_row(self, info, counter):
        """Add information in row"""
        self.table_info.insertRow(counter)
        filed_item = QtWidgets.QTableWidgetItem(f"{info[0]}")
        filed_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.table_info.setItem(counter, 0, filed_item)
        value_item = QtWidgets.QTableWidgetItem(f"{info[1]}")
        value_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.table_info.setItem(counter, 1, value_item)
        counter += 1

    def fill_table_info(self, picture_header, picture_info):
        """Fill table info"""
        counter = 0
        for info in picture_header:
            self._add_info_in_row(info, counter)
        for info in picture_info:
            self._add_info_in_row(info, counter)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    bmp = Window()
    sys.exit(app.exec_())
