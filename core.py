"""Module that implements the reading data of the program"""
from struct import unpack


class BitMapFileHeader:
    """BITMAPFILEHEADER structure class """

    def __init__(self):
        self.type = None
        self.size = None
        self.reserved_1 = None
        self.reserved_2 = None
        self.off_bits = None
        self.version = None

    def __iter__(self):
        yield ' Type: ', self.type
        yield ' Size: ', f'{self.size} bytes'
        yield ' Version: ', self.version
        yield ' OffBits: ', f'{self.off_bits} bytes'

    def __str__(self):
        result = '\nBITMAPFILEHEADER: \n'
        for field in self.__iter__():
            result += f'{field[0]}{field[1]}\n'
        return result

    def __eq__(self, other):
        return self.type == other.type and self.size == other.size and self.reserved_1 == other.reserved_1 \
               and self.reserved_2 == other.reserved_2 and self.off_bits == other.off_bits \
               and self.version == other.version


def read_bitmap_file_header(picture):
    """Read from file BITMAPFILEHEADER structure"""
    picture_header = BitMapFileHeader()
    picture_header.type = picture[:2].decode('utf-8')
    if picture_header.type != 'BM':
        raise TypePictureException('This picture is not BMP file')
    picture_header.size = unpack('<I', picture[0x2:0x2 + 4])[0]
    picture_header.reserved_1 = unpack('<H', picture[0x6:0x6 + 2])[0]
    picture_header.reserved_2 = unpack('<H', picture[0x8:0x8 + 2])[0]
    if picture_header.reserved_1 != 0 or picture_header.reserved_2 != 0:
        raise ReservedFieldsException('Reserved fields must contain zeros')
    picture_header.off_bits = unpack('<I', picture[0xa:0xa + 4])[0]
    version_size = unpack('<I', picture[0xe:0xe + 4])[0]
    picture_header.version = PICTURE_VERSION.get(version_size, "Undefined")
    return picture_header


class BitMapCoreInfo:
    """BITMAPCOREINFO structure class"""

    def __init__(self):
        self.version = None
        self.structure_size = None
        self.width = None
        self.height = None
        self.planes = None
        self.bit_count = None

    def __iter__(self):
        yield ' Structure Size: ', f'{self.structure_size} bytes'
        yield ' Width: ', f'{self.width} pixels'
        yield ' Height: ', f'{self.height} pixels'
        yield ' Planes: ', self.planes
        yield ' Bit Count: ', f'{self.bit_count} bits per pixels'

    def __str__(self):
        result = 'BITMAPCOREINFO: \n'
        for field in self.__iter__():
            result += f'{field[0]}{field[1]}\n'
        return result

    def __eq__(self, other):
        return self.version == other.version and self.structure_size == other.structure_size \
               and self.width == other.width and self.height == other.height \
               and self.planes == other.planes and self.bit_count == other.bit_count


def read_bitmap_core_info(picture):
    """Read from file BITMAPCOREINFO structure"""
    info = BitMapCoreInfo()
    info.version = 'CORE'
    info.structure_size = unpack('<I', picture[0x0e:0x0e + 4])[0]
    info.width = unpack('<H', picture[0x12:0x12 + 2])[0]
    info.height = unpack('<H', picture[0x14:0x14 + 2])[0]
    info.planes = unpack('<H', picture[0x16:0x16 + 2])[0]
    if info.planes != 1:
        raise PlanesFieldException('In BMP file in field "planes" the value is only 1')
    info.bit_count = unpack('<H', picture[0x18:0x18 + 2])[0]
    if info.bit_count == 0 or info.bit_count == 16 or info.bit_count == 32 \
            or info.bit_count == 48 or info.bit_count == 64:
        raise BitCountFieldException('Unacceptable number of bits per pixel')
    return info


class BitMapVersion3Info(BitMapCoreInfo):
    """BITMAPV3INFO structure class"""

    def __init__(self):
        super().__init__()
        self.compression = None
        self.size_image = None
        self.x_pixels_per_meter = None
        self.y_pixels_per_meter = None
        self.color_used = None
        self.color_important = None
        self.red_mask = None
        self.green_mask = None
        self.blue_mask = None
        self.alpha_mask = None

    def default_masks(self):
        """Set default masks"""
        if self.bit_count == 16:
            self.red_mask = 0x7C00
            self.green_mask = 0x03e0
            self.blue_mask = 0x001f
            self.alpha_mask = 0x000
        elif self.bit_count == 32:
            self.red_mask = 0x00ff0000
            self.green_mask = 0x0000ff00
            self.blue_mask = 0x000000ff
            self.alpha_mask = 0x00000000

    def __iter__(self):
        yield from super().__iter__()
        yield ' Compression: ', self.compression
        yield ' Pixel Data Size: ', f'{self.size_image} bytes'
        yield ' Pixels Per Meter on X: ', f'{self.x_pixels_per_meter} pixels'
        yield ' Pixels Per Meter on Y: ', f'{self.y_pixels_per_meter} pixels'
        yield ' Color Table Size: ', f'{self.color_used} cells'
        yield ' Color Important: ',  f'{self.color_important} cells'
        if self.compression == 3 or self.compression == 6:
            yield ' Red Mask: ', self.red_mask
            yield ' Green Mask: ', self.green_mask
            yield ' Blue Mask: ', self.blue_mask
            yield ' Alpha Mask: ', self.alpha_mask

    def __str__(self):
        result = 'BITMAPV3INFO: \n'
        for field in self.__iter__():
            result += f'{field[0]}{field[1]}\n'
        return result

    def __eq__(self, other):
        return super.__eq__(self, other) and self.compression == other.compression \
               and self.size_image == other.size_image and self.x_pixels_per_meter == other.x_pixels_per_meter \
               and self.y_pixels_per_meter == other.y_pixels_per_meter and self.color_used == other.color_used \
               and self.color_important == other.color_important and self.red_mask == other.red_mask \
               and self.green_mask == other.green_mask and self.blue_mask == other.blue_mask \
               and self.alpha_mask == other.alpha_mask


def read_bitmap_version_3_info(picture, info=None):
    """Read from file BITMAPV3INFO structure"""
    if info is None:
        info = BitMapVersion3Info()
        info.version = 3
    info.structure_size = unpack('<I', picture[0xe:0xe + 4])[0]
    info.width = unpack('<i', picture[0x12:0x12 + 4])[0]
    info.height = unpack('<i', picture[0x16:0x16 + 4])[0]
    info.planes = unpack('<H', picture[0x1a:0x1a + 2])[0]
    if info.planes != 1:
        raise PlanesFieldException('In BMP file in field "planes" the value is only 1')
    info.bit_count = unpack('<H', picture[0x1c:0x1c + 2])[0]
    if info.bit_count == 0:
        raise BitCountFieldException('Pixel data is stored in the format JPEG or PNG')
    info.compression = unpack('<I', picture[0x1e:0x1e + 4])[0]
    if info.compression == 4 or info.compression == 5:
        raise CompressionFieldException('Pixel data is stored in the format JPEG or PNG')
    info.size_image = unpack('<I', picture[0x22:0x22 + 4])[0]
    info.x_pixels_per_meter = unpack('<I', picture[0x26:0x26 + 4])[0]
    info.y_pixels_per_meter = unpack('<I', picture[0x2a:0x2a + 4])[0]
    info.color_used = unpack('<I', picture[0x2e:0x2e + 4])[0]
    info.color_important = unpack('<I', picture[0x32:0x32 + 4])[0]
    if info.color_used == 0 and info.bit_count <= 8:
        info.color_used = 2 ** info.bit_count
    if info.color_important == 0:
        info.color_important = info.color_used
    if info.compression == 3 or info.compression == 6:
        info.red_mask = unpack('<I', file[0x36:0x36 + 4])[0]
        info.green_mask = unpack('<I', file[0x3a:0x3a + 4])[0]
        info.blue_mask = unpack('<I', file[0x3e:0x3e + 4])[0]
        info.alpha_mask = unpack('<I', file[0x42:0x42 + 4])[0]
    return info


class BitMapVersion4Info(BitMapVersion3Info):
    """BITMAPV4INFO structure class"""

    def __init__(self):
        super().__init__()
        self.cs_type = None

    def __iter__(self):
        yield from super().__iter__()
        yield ' Color Space Type: ', self.cs_type

    def __str__(self):
        result = 'BITMAPV4INFO: \n'
        for field in self.__iter__():
            result += f'{field[0]}{field[1]}\n'
        return result

    def __eq__(self, other):
        return super.__eq__(self, other) and self.cs_type == other.cs_type


def read_bitmap_version_4_info(picture, info=None):
    """Read from file BITMAPV4INFO structure"""
    if info is None:
        info = BitMapVersion4Info()
        info.version = 4
    info = read_bitmap_version_3_info(picture, info)
    cs_type = unpack('<4s', picture[0x46:0x46 + 4])[0]
    if cs_type != b'\x00\x00\x00\x00':
        info.cs_type = cs_type.decode("utf-8")
    else:
        info.cs_type = 0
    return info


class BitMapVersion5Info(BitMapVersion4Info):
    """BITMAPCV5INFO structure class"""

    def __init__(self):
        super().__init__()
        self.intent = None
        self.profile_data = None
        self.profile_size = None
        self.reserved = None

    def __iter__(self):
        yield from super().__iter__()
        yield ' Intent: ', self.intent
        yield ' Profile Data: ', f'{self.profile_data} bytes'
        yield ' Profile Size: ', f'{self.profile_size} bytes'

    def __str__(self):
        result = 'BITMAPV5INFO: \n'
        for field in self.__iter__():
            result += f'{field[0]}{field[1]}\n'
        return result

    def __eq__(self, other):
        return super.__eq__(self, other) and self.intent == other.intent and self.profile_data == other.profile_data \
               and self.profile_size == other.profile_size and self.reserved == other.reserved


def read_bitmap_version_5_info(picture, info=None):
    """Read from file BITMAPV5INFO structure"""
    if info is None:
        info = BitMapVersion5Info()
        info._version = 5
    info = read_bitmap_version_4_info(picture, info)
    info.intent = unpack('<I', picture[0x7a:0x7a + 4])[0]
    info.profile_data = unpack('<I', picture[0x7e:0x7e + 4])[0]
    info.profile_size = unpack('<I', picture[0x82:0x82 + 4])[0]
    info.reserved = unpack('<I', picture[0x86:0x86 + 4])[0]
    if info.reserved != 0:
        raise ReservedFieldsException('Reserved fields must contain zeros')
    return info


def get_color_table(picture, info: BitMapVersion3Info):
    """Get palette from picture"""
    color_table = []
    for index in range(info.color_used):
        offset = 0x36 + index * 4  # We get palette only for bit count <= 8
        color = picture[offset:offset + 3]
        red = color[2]
        green = color[1]
        blue = color[0]
        color_table.append((red, green, blue))
    return color_table


def open_picture(picture_name):
    """Open the picture"""
    with open(picture_name, 'rb') as picture:
        return picture.read()


def select_info(picture, file_header):
    """Select read for the correct version"""
    return ACTIONS_FOR_VERSION.get(file_header.version)(picture)


class TypePictureException(Exception):
    """An error occurred while parsing the TYPE field"""
    pass


class ReservedFieldsException(Exception):
    """An error occurred while parsing the RESERVED field"""
    pass


class StructureSizeException(Exception):
    """And error occurred while parsing th STRUCTURE SIZE field"""
    pass


class PlanesFieldException(Exception):
    """An error occurred while parsing the PLANES field"""
    pass


class BitCountFieldException(Exception):
    """An error occurred while parsing the BITCOUNT field"""
    pass


class CompressionFieldException(Exception):
    """An error occurred while parsing the COMPRESSION field"""
    pass


PICTURE_VERSION = {
    12: 'CORE',
    40: 3,
    108: 4,
    124: 5
}

ACTIONS_FOR_VERSION = {
    'CORE': read_bitmap_core_info,
    3: read_bitmap_version_3_info,
    4: read_bitmap_version_4_info,
    5: read_bitmap_version_5_info
}
