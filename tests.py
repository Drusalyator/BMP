import unittest
from core import *


class StructureTest(unittest.TestCase):

    def test_picture_header(self):
        """Test class 'BitMapFileHeader' and method 'read_bitmap_file_header'"""
        core_picture = open_picture("test_image\image_test_1.bmp")
        picture_header = read_bitmap_file_header(core_picture)
        test_header = BitMapFileHeader()
        test_header.type = "BM"
        test_header.version = "CORE"
        test_header.reserved_1 = 0
        test_header.reserved_2 = 0
        test_header.size = 390542
        test_header.off_bits = 54
        self.assertEqual(picture_header, test_header)

    def test_core_info(self):
        """Test class 'BitMapCoreInfo' and method 'read_bitmap_core_info'"""
        core_picture = open_picture("test_image\image_test_1.bmp")
        picture_core_info = read_bitmap_core_info(core_picture)
        test_core_info = BitMapCoreInfo()
        test_core_info.version = "CORE"
        test_core_info.bit_count = 24
        test_core_info.structure_size = 12
        test_core_info.width = 354
        test_core_info.height = 367
        test_core_info.planes = 1
        self.assertEqual(picture_core_info, test_core_info)

    def test_version_3_info(self):
        """Test class 'BitMapVersion3Info' and method 'read_bitmap_version_3_info'"""
        version_3_picture = open_picture("test_image\image_test_2.bmp")
        picture_v3_info = read_bitmap_version_3_info(version_3_picture)
        test_v3_info = BitMapVersion3Info()
        test_v3_info.planes = 1
        test_v3_info.height = 395
        test_v3_info.width = 572
        test_v3_info.bit_count = 24
        test_v3_info.version = 3
        test_v3_info.color_used = 0
        test_v3_info.compression = 0
        test_v3_info.y_pixels_per_meter = 30741
        test_v3_info.x_pixels_per_meter = 9041
        test_v3_info.size_image = 677820
        test_v3_info.color_important = 0
        self.assertEqual(picture_v3_info, test_v3_info)

    def test_version_4_info(self):
        """Test class 'BitMapVersion4Info' and method 'read_bitmap_version_4_info'"""
        version_4_picture = open_picture("test_image\image_test_2.bmp")
        picture_v4_info = read_bitmap_version_4_info(version_4_picture)
        test_v4_info = BitMapVersion4Info()
        test_v4_info.planes = 1
        test_v4_info.height = 395
        test_v4_info.width = 572
        test_v4_info.bit_count = 24
        test_v4_info.version = 3
        test_v4_info.color_used = 0
        test_v4_info.compression = 0
        test_v4_info.y_pixels_per_meter = 30741
        test_v4_info.x_pixels_per_meter = 9041
        test_v4_info.size_image = 677820
        test_v4_info.color_important = 0
        test_v4_info.cs_type = 0
        self.assertEqual(picture_v4_info, test_v4_info)

    def test_version_5_info(self):
        """Test class 'BitMapVersion5Info' and method 'read_bitmap_version_5_info'"""
        version_5_picture = open_picture("test_image\image_test_2.bmp")
        picture_v5_info = read_bitmap_version_5_info(version_5_picture)
        test_v5_info = BitMapVersion5Info()
        test_v5_info.planes = 1
        test_v5_info.height = 395
        test_v5_info.width = 572
        test_v5_info.bit_count = 24
        test_v5_info.version = 3
        test_v5_info.color_used = 0
        test_v5_info.compression = 0
        test_v5_info.y_pixels_per_meter = 30741
        test_v5_info.x_pixels_per_meter = 9041
        test_v5_info.size_image = 677820
        test_v5_info.color_important = 0
        test_v5_info.cs_type = 0
        test_v5_info.intent = 4206867
        test_v5_info.profile_data = 25605
        test_v5_info.profile_size = 8941130
        test_v5_info.reserved = 0
        self.assertEqual(picture_v5_info, test_v5_info)

    def test_color_table(self):
        """Test method 'get_color_table'"""
        picture = open_picture("test_image\image_test_3.bmp")
        header = read_bitmap_file_header(picture)
        info = select_info(picture, header)
        color_table = get_color_table(picture, info)
        self.assertEqual(color_table, [(0, 0, 0), (255, 255, 255)])

    def test_color_mask(self):
        picture = open_picture("test_image\image_test_4.bmp")
        info = BitMapVersion3Info()
        info.bit_count = 16
        info.default_masks()
        self.assertEqual(info.red_mask, 31744)
        self.assertEqual(info.green_mask, 992)
        self.assertEqual(info.blue_mask, 31)
        self.assertEqual(info.alpha_mask, 0)
        info = read_bitmap_version_3_info(picture)
        self.assertEqual(info.red_mask, 58909)
        self.assertEqual(info.green_mask, 46566)
        self.assertEqual(info.blue_mask, 7605)
        self.assertEqual(info.alpha_mask, 498437965)

    def test_print(self):
        core_picture = open_picture("test_image\image_test_1.bmp")
        picture_header = read_bitmap_file_header(core_picture)
        self.assertEqual(picture_header.__str__(), "\nBITMAPFILEHEADER: \n Type: BM\n Size: 390542 bytes"
                                                   "\n Version: CORE\n OffBits: 54 bytes\n")
        core_picture = open_picture("test_image\image_test_1.bmp")
        picture_core_info = read_bitmap_core_info(core_picture)
        self.assertEqual(picture_core_info.__str__(), "BITMAPCOREINFO: \n Structure Size: 12 bytes\n "
                                                      "Width: 354 pixels\n Height: 367 pixels\n Planes: 1\n "
                                                      "Bit Count: 24 bits per pixels\n")


if __name__ == '__main__':
    unittest.main()
