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

        self.histogram = Histogram()

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
        show_red_histogram.triggered.connect(
            lambda: self._show_histogram(self.renderer.red_histogram))
        show_green_histogram = QtWidgets.QAction("Green histogram", self)
        show_green_histogram.triggered.connect(
            lambda: self._show_histogram(self.renderer.green_histogram))
        show_blue_histogram = QtWidgets.QAction("Blue histogram", self)
        show_blue_histogram.triggered.connect(
            lambda: self._show_histogram(self.renderer.blue_histogram))
        show_general_histogram = QtWidgets.QAction("General histogram", self)
        show_general_histogram.triggered.connect(
            lambda: self._show_histogram(self.renderer.general_histogram))

        picture_menu.addAction(show_info)
        picture_menu.addAction(show_red_histogram)
        picture_menu.addAction(show_green_histogram)
        picture_menu.addAction(show_blue_histogram)
        picture_menu.addAction(show_general_histogram)
        picture_menu.addAction(close_app)

        self.hide()

    def _show_histogram(self, histogram_array):
        """Show histogram"""
        self.histogram.draw_histogram(histogram_array)
        if self.histogram.isHidden():
            self.histogram.show()
        else:
            self.histogram.hide()
            self.histogram.show()

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
            self.renderer = DrawBMP(self.picture, self.picture_header, self.picture_info, self.color_table)
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


class DrawBMP(QtWidgets.QWidget):
    """Class drawing BMP"""
    def __init__(self, picture, picture_header, picture_info, color_table):
        super().__init__()
        self.picture = picture
        self.picture_header = picture_header
        self.picture_info = picture_info
        self.color_table = color_table
        self.pixmap = None
        self.ready = False
        self.byte_offset = 0
        self.all_bit_count = [1, 2, 4, 8, 24]
        self.get_pixels_color = {1: self._less_then_8_bit_color, 2: self._less_then_8_bit_color,
                                 4: self._less_then_8_bit_color, 8: self._8_bit_color, 24: self._24_bit_color}
        self._init_histograms_data()

    def _init_histograms_data(self):
        """Init histogram data"""
        self.red_histogram = []
        self._add_array(self.red_histogram)
        self.green_histogram = []
        self._add_array(self.green_histogram)
        self.blue_histogram = []
        self._add_array(self.blue_histogram)
        self.general_histogram = []
        self._add_array(self.general_histogram)

    @staticmethod
    def _add_array(array):
        """Fill array in gistogram data"""
        for index in range(256):
            array.append(0)

    def _update_histogram_data(self, color):
        """Update histogram data"""
        red_color = color[0]
        self.red_histogram[red_color] += 1
        green_color = color[1]
        self.green_histogram[green_color] += 1
        blue_color = color[2]
        self.blue_histogram[blue_color] += 1
        pixel_brightness = int(math.floor(0.299 * red_color + 0.587 * green_color + 0.114 * blue_color))
        self.general_histogram[pixel_brightness] += 1

    def _rendering(self):
        """Start rendering the picture"""
        self.pixmap = QtGui.QPixmap(self.picture_info.width, self.picture_info.height)
        painter = QtGui.QPainter()
        painter.begin(self.pixmap)
        if self.picture_info.bit_count in self.all_bit_count:
            pixel_iterator = self._pixels_iterator()
            for pixel in pixel_iterator:
                coordinates = pixel[0]
                color = pixel[1]
                painter.fillRect(*coordinates, 1, 1, QtGui.QColor(*color))
        else:
            raise BitCountFieldException("This bit count not supported")
        painter.end()

    def _pixels_iterator(self):
        """Get pixels iterator"""
        row = self.picture_info.height - 1
        local_offset = 0
        offset = self.picture_header.off_bits
        while row >= 0:
            color, offset = self.get_pixels_color.get(self.picture_info.bit_count)(offset)
            x = local_offset
            y = row
            self._update_histogram_data(color)
            yield (x, y), color
            local_offset += 1
            if local_offset >= self.picture_info.width:
                total_offset = offset - self.picture_header.off_bits
                while total_offset % 4 != 0:
                    offset += 1
                    total_offset += 1
                row -= 1
                local_offset = 0
                self.byte_offset = 0

    def _less_then_8_bit_color(self, offset):
        """Get less then 8 bit color"""
        if self.byte_offset == 8:
            offset += 1
            self.byte_offset = 0
        if self.byte_offset == 0:
            self.byte = '{:08b}'.format(unpack('B', self.picture[offset:offset + 1])[0])
        index_in_color_table = int(self.byte[self.byte_offset:self.byte_offset + self.picture_info.bit_count], 2)
        self.byte_offset += self.picture_info.bit_count
        color = self.color_table[index_in_color_table]
        return color, offset

    def _8_bit_color(self, offset):
        """Get 8 bit color"""
        index_in_color_table = unpack('B', self.picture[offset:offset + 1])[0]
        color = self.color_table[index_in_color_table]
        return color, offset + 1

    def _24_bit_color(self, offset):
        blue = unpack('B', self.picture[offset:offset + 1])[0]
        green = unpack('B', self.picture[offset + 1:offset + 2])[0]
        red = unpack('B', self.picture[offset + 2:offset + 3])[0]
        return (red, green, blue), offset + 3

    def paintEvent(self, event):
        """Paint event"""
        if self.pixmap is not None:
            self._draw_pixmap()
            return
        try:
            self._rendering()
        except BitCountFieldException as exception:
            QtWidgets.QMessageBox.warning(self, "Error", "{}".format(exception), QtWidgets.QMessageBox.Ok)
        if not self.ready:
            self._draw_pixmap()
            self.ready = True

    def _draw_pixmap(self):
        """Draw ready pixmap"""
        painter = QtGui.QPainter()
        geometry = self.geometry()
        painter.begin(self)
        painter.drawPixmap((geometry.width() - self.picture_info.width) / 2,
                           (geometry.height() - self.picture_info.height) / 2,
                           self.pixmap)
        painter.end()


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


class Histogram(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.ready = False
        self.setFixedSize(530, 320)
        self.hide()

    def draw_histogram(self, histogram_array):
        self.ready = False
        self.pixmap = None
        self.pixmap = QtGui.QPixmap(512, 300)
        self.pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter()
        painter.begin(self.pixmap)
        maximum = 0
        for point in histogram_array:
            if point > maximum:
                maximum = point
        if maximum > 250:
            factor = maximum / 250
        else:
            factor = 1
        painter.fillRect(0, 298, 512, 2, QtGui.QColor(0, 0, 0))
        for index in range(len(histogram_array)):
            height = int(histogram_array[index] / factor)
            painter.fillRect(index * 2, 298 - height, 2, height, QtGui.QColor(0, 0, 255))
        painter.end()

    def _draw_pixmap(self):
        """Draw ready pixmap"""
        painter = QtGui.QPainter()
        geometry = self.geometry()
        painter.begin(self)
        painter.drawPixmap((geometry.width() - 512) / 2, (geometry.height() - 300) / 2, self.pixmap)
        painter.end()

    def paintEvent(self, event):
        """Paint event"""
        if self.pixmap is not None:
            self._draw_pixmap()
            return


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    bmp = Window()
    sys.exit(app.exec_())
