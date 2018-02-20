"""This file implements the graphical version of program"""
import sys
import math
from core import *
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class Window(QtWidgets.QMainWindow):
    """Main window"""

    def __init__(self, picture_name=None):
        super().__init__()
        self._init_window()
        self.picture_name = picture_name
        self.color_table = None
        self._get_picture_structure(self.picture_name)

    def _init_window(self):
        """Initialize window"""
        self.setWindowTitle("BMP structure")

        self.table_info = TableInfo()
        self.table_info.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.table_info.move(30, 100)

        menu = self.menuBar()
        picture_menu = menu.addMenu("Picture")

        close_app = QtWidgets.QAction("Close", self)
        close_app.setShortcut("Ctrl+Q")
        close_app.triggered.connect(lambda: sys.exit())

        show_info = QtWidgets.QAction("Show info", self)
        show_info.setShortcut("Ctrl+I")
        show_info.triggered.connect(
            lambda: self.table_info.show() if self.table_info.isHidden() else self.table_info.hide())

        show_red_histogram = QtWidgets.QAction("Red histogram", self)
        show_green_histogram = QtWidgets.QAction("Green histogram", self)
        show_blue_histogram = QtWidgets.QAction("Blue histogram", self)

        picture_menu.addAction(show_info)
        picture_menu.addAction(show_red_histogram)
        picture_menu.addAction(show_green_histogram)
        picture_menu.addAction(show_blue_histogram)
        picture_menu.addAction(close_app)

        self.hide()

    def _get_picture_structure(self, picture_name=None):
        """Get information about picture"""
        if picture_name is None or picture_name == "":
            picture_name = QtWidgets.QFileDialog.getOpenFileName(self, "Load picture", filter="Data (*.bmp)")[0]
            self.picture_name = picture_name
        try:
            with open(self.picture_name, 'rb'):
                self.picture = open_picture(self.picture_name)
                self.picture_header = read_bitmap_file_header(self.picture)
                self.picture_info = select_info(self.picture, self.picture_header)
                if self.picture_info.bit_count <= 8:
                    self.color_table = get_color_table(self.picture, self.picture_info)
        except Exception as exception:
            QtWidgets.QMessageBox.warning(self, "Error", "Error: {}".format(exception), QtWidgets.QMessageBox.Ok)
            sys.exit("Incorrect picture")
        else:
            self.renderer = BmpRenderer(self.picture, self.picture_header, self.picture_info, self.color_table)
            self.setCentralWidget(self.renderer)
            self.showMaximized()
            self._show_table_info(self.picture_header, self.picture_info)

    def _show_table_info(self, picture_header, picture_info):
        """Show table with information about picture"""
        try:
            self.table_info.fill_table_info(picture_header, picture_info)
        except Exception as exception:
            QtWidgets.QMessageBox.warning(self, "Error", "Can't show info about picture: {}".format(exception),
                                          QtWidgets.QMessageBox.Ok)
        else:
            self.table_info.show()


class BmpRenderer(QtWidgets.QWidget):
    def __init__(self, file, header, bitmap_info, color_table, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.pixmap_cache = None
        self.has_drawn = False
        self.min_size = 300
        self.bitmap_info = bitmap_info
        self.file = file
        self.header = header
        self.byte_count = bitmap_info.bit_count / 8 if bitmap_info.bit_count >= 8 else 1
        self.color_table = color_table
        self.byte_offset = 0

    def paintEvent(self, e):
        if self.pixmap_cache is not None:
            self.draw_cached_picture()
            return
        self.render_explicitly()
        if not self.has_drawn:
            self.draw_cached_picture()
            self.has_drawn = True

    def draw_cached_picture(self):
        qp = QtGui.QPainter()
        geom = self.geometry()
        qp.begin(self)
        qp.resetTransform()
        qp.drawPixmap((geom.width() - self.bitmap_info.width) / 2,
                      (geom.height() - self.bitmap_info.height) / 2,
                      self.pixmap_cache)
        qp.end()

    def render_explicitly(self):
        self.pixmap_cache = QtGui.QPixmap(self.bitmap_info.width, self.bitmap_info.height)
        self.pixmap_cache.fill(QtCore.Qt.transparent)
        qp = QtGui.QPainter()
        qp.begin(self.pixmap_cache)
        self.render_picture(qp, self.file, 1)
        qp.end()

    def render_picture(self, painter):
        pixel_extractor = self.get_pixels()
        for pixel in pixel_extractor:
            coord, color = pixel
            painter.fillRect(*coord, pixel_size, pixel_size, QtGui.QColor(*color))

    def get_pixels(self, pixel_size=1):
        row_number = self.bitmap_info.height - 1
        local_pixel_offset = 0
        pixel_offset = self.header.off_bits
        while row_number >= 0:
            color, pixel_offset = self.get_24_bit_color(pixel_offset)
            x = local_pixel_offset * pixel_size
            y = row_number * pixel_size
            yield (x, y), color
            local_pixel_offset += 1
            if local_pixel_offset >= self.bitmap_info.width:
                total_offset = pixel_offset - self.header.off_bits
                while total_offset % 4 != 0:
                    local_pixel_offset += 1
                    pixel_offset += 1
                    total_offset += 1
                row_number -= 1
                local_pixel_offset = 0
                self.byte_offset = 0

    def get_24_bit_color(self, offset):
        blue = unpack('B', self.file[offset:offset + 1])[0]
        green = unpack('B', self.file[offset + 1:offset + 2])[0]
        red = unpack('B', self.file[offset + 2:offset + 3])[0]
        return (red, green, blue), offset + 3


class TableInfo(QtWidgets.QWidget):
    """Table with information about picture"""

    def __init__(self):
        """Initialize class"""
        super().__init__()
        self._init_table()

    def _init_table(self):
        """Initialize widgets on a record table"""
        self.setWindowTitle("Picture Info")
        self.setFixedSize(265, 400)

        self.table_info = QtWidgets.QTableWidget(self)
        self.table_info.setColumnCount(2)
        self.table_info.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        item = QtWidgets.QTableWidgetItem("Field")
        self.table_info.setHorizontalHeaderItem(0, item)

        item = QtWidgets.QTableWidgetItem("Value")
        self.table_info.setHorizontalHeaderItem(1, item)

        self.ok_button = QtWidgets.QPushButton("Ok", self)
        self.ok_button.clicked.connect(self.hide)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table_info)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

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
        return counter

    def fill_table_info(self, picture_header, picture_info):
        """Fill table info"""
        counter = 0
        for info in picture_header:
            counter = self._add_info_in_row(info, counter)
        for info in picture_info:
            counter = self._add_info_in_row(info, counter)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    bmp = Window()
    sys.exit(app.exec_())
