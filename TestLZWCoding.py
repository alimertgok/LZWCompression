# import os
# import unittest
# from PIL import Image
# import numpy as np
#
# from LZWClass import LZWCoding
#
#
# class TestLZWCoding(unittest.TestCase):
#     def setUp(self):
#         self.text_file = "test_text_file.txt"
#         with open(self.text_file, "w", encoding="utf-8") as file:
#             file.write("abababab")
#
#         # Create a sample image file
#         self.image_file = "test_image.png"
#         img = Image.new("RGB", (10, 10), color="red")
#         img.save(self.image_file)
#
#     def tearDown(self):
#         # Clean up test files
#         if os.path.exists(self.text_file):
#             os.remove(self.text_file)
#         if os.path.exists(self.image_file):
#             os.remove(self.image_file)
#
#     def test_initialization_text(self):
#         lzw = LZWCoding(self.text_file, "text")
#         self.assertEqual(lzw.path, self.text_file)
#         self.assertEqual(lzw.data_type, "text")
#         self.assertEqual(lzw.filename, "test_text_file")
#         self.assertEqual(lzw.file_extension, ".txt")
#         self.assertGreater(lzw.file_size, 0)
#
#     def test_initialization_image(self):
#         lzw = LZWCoding(self.image_file, "image")
#         self.assertEqual(lzw.path, self.image_file)
#         self.assertEqual(lzw.data_type, "image")
#         self.assertEqual(lzw.filename, "test_image")
#         self.assertEqual(lzw.file_extension, ".png")
#         self.assertGreater(lzw.file_size, 0)
#         self.assertIsNotNone(lzw.img)
#
#     def test_compress(self):
#         lzw = LZWCoding(self.text_file, "text")
#         with open(lzw.path, "r", encoding="utf-8") as file:
#             text_data = file.read()
#         compressed_data = lzw.compress(text_data)
#         self.assertIsInstance(compressed_data, list)
#         self.assertTrue(all(isinstance(x, int) for x in compressed_data))
#
#     def test_decompress(self):
#         lzw = LZWCoding(self.text_file, "text")
#         with open(lzw.path, "r", encoding="utf-8") as file:
#             text_data = file.read()
#         compressed_data = lzw.compress(text_data)
#         decompressed_data = lzw.decompress(compressed_data.copy())
#         self.assertEqual(decompressed_data, text_data)
#
#     def test_pad_encoded_text(self):
#         lzw = LZWCoding(self.text_file, "text")
#         encoded_text = "110101"
#         padded_encoded_text = lzw.pad_encoded_text(encoded_text)
#         self.assertEqual(len(padded_encoded_text) % 8, 0)
#         self.assertTrue(padded_encoded_text.startswith("00000010"))  # Padding info for 2 zeros
#
#     def test_get_byte_array(self):
#         lzw = LZWCoding(self.text_file, "text")
#         padded_encoded_text = "0000001011010100"  # Padding info: 2, Padded text: 11010100
#         byte_array = lzw.get_byte_array(padded_encoded_text)
#         self.assertEqual(byte_array, [0b00000010, 0b11010100])
#
#     def test_int_array_to_binary_string(self):
#         lzw = LZWCoding(self.text_file, "text")
#         int_array = [2, 5]
#         binary_string = lzw.int_array_to_binary_string(int_array)
#         self.assertEqual(binary_string, "000000010000000101")  # 9 bits per code
#
#     def test_remove_padding(self):
#         lzw = LZWCoding(self.text_file, "text")
#         padded_encoded_text = "0000001011010100"  # Padding info: 2, Padded text: 11010100
#         int_codes = lzw.remove_padding(padded_encoded_text)
#         self.assertEqual(int_codes, [int("110101", 2)])
#
#
# if __name__ == "__main__":
#     unittest.main()