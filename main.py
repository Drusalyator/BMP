#!/usr/bin/env python3
import sys
import argparse

try:
    from core import *
    from gui import *
except Exception as exception:
    sys.exit("Some program module not found: {}".format(exception))

try:
    from PyQt5.QtWidgets import QApplication
except Exception as exception:
    sys.exit("PyQt5 not found {}".fomat(exception))


__version__ = '1.0'
__author__ = 'Gridin Andrey'


def parse_args():
    """Arguments parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="file to get the structure")
    parser.add_argument("-g", "--gui", action="store_true", help="enable gui")
    return parser.parse_args()


def input_picture_name():
    """Input picture name"""
    picture_name = input("Input Picture Name: ")
    while picture_name == '':
        picture_name = input("Input Picture Name: ")
    return picture_name


def console_version(picture_name):
    """Run console version of program"""
    picture = open_picture(picture_name)
    picture_header = read_bitmap_file_header(picture)
    bitmap_info = select_info(picture, picture_header)
    print(picture_header)
    print(bitmap_info)


def graphical_version(picture_name):
    """Run graphical version of program"""
    app = QtWidgets.QApplication([])
    bmp = Window(picture_name)
    sys.exit(app.exec_())


def main():
    """Entry point"""
    try:
        args = parse_args()
        if args.gui:
            graphical_version(args.file)
        else:
            if args.file is not None:
                picture_name = args.file
            else:
                picture_name = input_picture_name()
            console_version(picture_name)
    except Exception as e:
        print("Error! " + str(e))


if __name__ == '__main__':
    main()
