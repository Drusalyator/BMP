# Program "BMP structure"

Version 1.0

Author: Gridin Andrey

## Specification

This application parses structure of BMP file. In the console version displays only the internal structure of the file. In the graphical version, the image is rendered and you can see the image histograms

## Demands

- python version 3.5
- PyQt  version 5

## Composition

- Logic of program: `core.py`
- Tests: `\tests`
- Entry point `main.py`
- gui: `gui.py`


## Graphical version

Start-up example `python main.py -g` or `python main.py --gui` 

## Console mode

Start-up example python `python main.py` or with file `python main.py -f FILENAME`

## Some details

Code coverage of the code

`core.py       138      2       99%`

