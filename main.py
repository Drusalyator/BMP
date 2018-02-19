#!/usr/bin/env python3


import sys

if sys.version < (3, 4):
    print('Use python version >= 3.5', file=sys.stderr)
    sys.exit()

import argparse
import logging

__version__ = '1.0'
__author__ = 'Gridin Andrey'




def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="file to get the structure")
    return parser.parse_args()


def input_picture_name():
    picture_name = input("Input Picture Name: ")
    while picture_name == '':
        picture_name = input("Input Picture Name: ")
    return picture_name


def console_version(picture_name):
    picture = open_picture(picture_name)
    picture_header = read_bitmap_file_header(picture)
    bitmap_info = select_info(picture, picture_header)
    print(picture_header)
    print(bitmap_info)


def main():
    try:
        args = parse_args()
        if args.file is not None:
            picture_name = args.file
        else:
            picture_name = input_picture_name()
        console_version(picture_name)
    except Exception as e:
        print("Error! " + str(e))


if __name__ == '__main__':
    main()
