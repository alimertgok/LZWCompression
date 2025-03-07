import os  # the os module is used for file and directory operations
import math  # the math module provides access to mathematical functions
from io import StringIO

import numpy as np

from image_tools import readPILimg, color2gray, PIL2np, red_values, green_values, blue_values, np2PIL, merge_image


# A class that implements the LZW compression and decompression algorithms as
# well as the necessary utility methods for text files.
# ------------------------------------------------------------------------------
class LZWCoding:
   # A constructor with two input parameters
   # ---------------------------------------------------------------------------
   def __init__(self, filename, data_type):
      # use the input parameters to set the instance variables
      self.filename = filename
      self.data_type = data_type   # e.g., 'text'
      # initialize the code length as None 
      # (the actual value is determined based on the compressed data)
      self.codelength = None


   def compute_difference_image(self, img_array):
      """Compute row-wise and column-wise differences."""
      diff_image = np.copy(img_array)

      # Row-wise differences (excluding first column)
      diff_image[:, 1:] -= img_array[:, :-1]

      # Column-wise differences (excluding first row)
      diff_image[1:, 0] -= img_array[:-1, 0]

      return diff_image

   def restore_original_image(self, diff_array):
      """Reconstruct the original image from the difference image."""

      if self.data_type == "colorimage":
         restored_image = np.copy(diff_array).astype(np.int32)
      else:
         restored_image = np.copy(diff_array)

      # Restore first column (önce ilk sütunu düzelt)
      for i in range(1, restored_image.shape[0]):
         restored_image[i, 0] += restored_image[i - 1, 0]

      # Restore first row and the rest of the image
      for i in range(restored_image.shape[0]):
         for j in range(1, restored_image.shape[1]):
            restored_image[i, j] += restored_image[i, j - 1]

      return restored_image

   def calculate_entropy(self, data_array):
      """Calculates entropy of an image or text data."""
      unique, counts = np.unique(data_array, return_counts=True)
      probabilities = counts / np.sum(counts)
      entropy = -np.sum(probabilities * np.log2(probabilities))
      return entropy

   # A method that compresses the contents of a text file to a binary output file 
   # and returns the path of the output file.
   # ---------------------------------------------------------------------------

   def compress_file(self):
      # Get the current directory where this script is located
      global original_entropy
      current_directory = os.path.dirname(os.path.realpath(__file__))

      # Define input and output file paths
      input_file = self.filename + '.txt' if self.data_type == "text" else self.filename
      input_path = os.path.join(current_directory, input_file)
      output_file = self.filename + '.bin'
      output_path = os.path.join(current_directory, output_file)

      # Variable to store the data to be compressed
      mytext = ""

      if self.data_type == "text":
         # Read the text file
         with open(input_path, 'r') as in_file:
            mytext = in_file.read().rstrip()

      elif self.data_type == "graylevelimage":
         # Open the grayscale image using your function
         img = readPILimg(input_path)
         img_gray = color2gray(img)  # Convert to grayscale
         img_gray.show()
         img_array = PIL2np(img_gray)  # Convert to numpy array
         nrows, ncols = img_array.shape
         print(f"Original Image Dimensions: {nrows} x {ncols}")

         # Obtain the difference image and save it
         diff_array = self.compute_difference_image(img_array)

         # Find shapes of diff_array
         diff_row, diff_col = diff_array.shape

         diff_string = "".join(chr(diff_array[i][j]) for i in range(diff_row) for j in range(diff_col))

         mytext = diff_string

         # Compute original entropy
         original_entropy = self.calculate_entropy(img_array)
         difference_entropy = self.calculate_entropy(diff_array)

      elif self.data_type == "colorimage":
         # Open the RGB image using your function
         img = readPILimg(input_path)

         img.show()

         # Extract RGB channel values using your functions
         red = red_values(img)
         green = green_values(img)
         blue = blue_values(img)

         # Convert RGB (lists) to numpy array
         red = np.array(red, dtype=np.uint8)
         green = np.array(green, dtype=np.uint8)
         blue = np.array(blue, dtype=np.uint8)


         # Ensure RGB are 2D arrays
         nrows, ncols = img.size[1], img.size[0]
         red = red.reshape((nrows, ncols))
         green = green.reshape((nrows, ncols))
         blue = blue.reshape((nrows, ncols))

         # Compute difference images for each channel
         red_diff = self.compute_difference_image(red)
         green_diff = self.compute_difference_image(green)
         blue_diff = self.compute_difference_image(blue)

         diff_row, diff_col = red_diff.shape # they all have the same shape

         # Convert difference arrays into strings for compression
         red_string = "".join(chr(red_diff[i, j]) for i in range(diff_row) for j in range(diff_col))
         green_string = "".join(chr(green_diff[i, j]) for i in range(diff_row) for j in range(diff_col))
         blue_string = "".join(chr(blue_diff[i, j]) for i in range(diff_row) for j in range(diff_col))

         # Merge RGB channels back into one image
         mytext = red_string + green_string + blue_string  # No merging here!

      else:
         print("Unknown data type!")
         return None

      # Encode the data using the LZW compression algorithm
      encoded_text_as_integers = self.encode(mytext)
      encoded_text = self.int_list_to_binary_string(encoded_text_as_integers)
      encoded_text = self.add_code_length_info(encoded_text)
      padded_encoded_text = self.pad_encoded_data(encoded_text)
      byte_array = self.get_byte_array(padded_encoded_text)

      # Write the compressed data to the output file
      with open(output_path, 'wb') as out_file:
         out_file.write(bytes(byte_array))

      # Compute and display compression details
      uncompressed_size = len(mytext)
      compressed_size = len(byte_array)
      compression_ratio = uncompressed_size / compressed_size if compressed_size != 0 else 0

      # Compute compressed entropy
      compressed_entropy = self.calculate_entropy(np.array(encoded_text_as_integers))

      print(f"{input_file} has been compressed into {output_file}.")
      print(f"Uncompressed Size: {uncompressed_size:,d} bytes")
      print(f"Code Length: {self.codelength}")
      print(f"Compressed Size: {compressed_size:,d} bytes")
      print(f"Compression Ratio: {compression_ratio:.2f}")
      # print(f"Original Entropy: {original_entropy:.2f} bits/pixel")
      # print(f"Difference Image Entropy: {difference_entropy:.2f} bits/pixel")
      # print(f"Compressed Entropy: {compressed_entropy:.2f} bits/pixel")

      return output_path

   # A method that encodes a text input into a list of integer values by using
   # the LZW compression algorithm and returns the resulting list.
   # ---------------------------------------------------------------------------
   def encode(self, uncompressed_data):
      # build the initial dictionary by mapping the characters in the extended 
      # ASCII table to their indexes
      dict_size = 256
      dictionary = {chr(i): i for i in range(dict_size)}

      # perform the LZW compression algorithm
      w = ''   # initialize a variable to store the current sequence
      result = []   # initialize a list to store the encoded values to output
      # iterate over each item (a character for text files) in the input data
      for k in uncompressed_data:
         # keep forming a new sequence until it is not in the dictionary
         wk = w + k
         if wk in dictionary:   # if wk exists in the dictionary
            w = wk   # update the sequence by adding the current item
         else:   # otherwise
            # add the code for w (the longest sequence found in the dictionary)
            # to the list that stores the encoded values
            result.append(dictionary[w])
            # add wk (the new sequence) to the dictionary
            dictionary[wk] = dict_size
            dict_size += 1
            # reset w to the current character
            w = k
      # add the code for the remaining sequence (if it exists) to the list that 
      # stores the encoded values (integer codes)
      if w:
         result.append(dictionary[w])
      
      # set the code length for compressing the encoded values based on the input 
      # data (by using the size of the resulting dictionary)
      self.codelength = math.ceil(math.log2(len(dictionary)))

      # return the encoded values (a list of integer dictionary values)
      return result

   # A method that converts the integer list returned by the compress method
   # into a binary string and returns the resulting string.
   # ---------------------------------------------------------------------------
   def int_list_to_binary_string(self, int_list):
      # initialize the binary string as an empty string
      bitstring = ''
      # concatenate each integer in the input list to the binary string
      for num in int_list:
         # using codelength bits to compress each value
         for n in range(self.codelength):
            if num & (1 << (self.codelength - 1 - n)):
               bitstring += '1'
            else:
               bitstring += '0'
      # return the resulting binary string
      return bitstring

   # A method that adds the code length to the beginning of the binary string
   # that corresponds to the compressed data and returns the resulting string.
   # (the compressed data should contain everything needed to decompress it)
   # ---------------------------------------------------------------------------
   def add_code_length_info(self, bitstring):
      # create a binary string that stores the code length as a byte
      codelength_info = '{0:08b}'.format(self.codelength)
      # add the code length info to the beginning of the given binary string
      bitstring = codelength_info + bitstring
      # return the resulting binary string
      return bitstring

   # A method for adding zeros to the binary string (the compressed data)
   # to make the length of the string a multiple of 8.
   # (This is necessary to be able to write the values to the file as bytes.)
   # ---------------------------------------------------------------------------
   def pad_encoded_data(self, encoded_data):
      # compute the number of the extra bits to add
      if len(encoded_data) % 8 != 0:
         extra_bits = 8 - len(encoded_data) % 8
         # add zeros to the end (padding)
         for i in range(extra_bits):
            encoded_data += '0'
      else:   # no need to add zeros
         extra_bits = 0
      # add a byte that stores the number of added zeros to the beginning of
      # the encoded data
      padding_info = '{0:08b}'.format(extra_bits)
      encoded_data = padding_info + encoded_data
      # return the resulting string after padding
      return encoded_data

   # A method that converts the padded binary string to a byte array and returns 
   # the resulting array. 
   # (This byte array will be written to a file to store the compressed data.)
   # ---------------------------------------------------------------------------
   def get_byte_array(self, padded_encoded_data):
      # the length of the padded binary string must be a multiple of 8
      if (len(padded_encoded_data) % 8 != 0):
         print('The compressed data is not padded properly!')
         exit(0)
      # create a byte array
      b = bytearray()
      # append the padded binary string to byte by byte
      for i in range(0, len(padded_encoded_data), 8):
         byte = padded_encoded_data[i : i + 8]
         b.append(int(byte, 2))
      # return the resulting byte array
      return b

   # A method that reads the contents of a compressed binary file, performs
   # decompression and writes the decompressed output to a text file.
   # ---------------------------------------------------------------------------
   def decompress_file(self):
      # Get the current directory where this program is located
      current_directory = os.path.dirname(os.path.realpath(__file__))

      # Define input and output file paths
      input_file = self.filename + '.bin'
      input_path = os.path.join(current_directory, input_file)
      # Determine the output file extension dynamically
      if self.data_type == "text":
         output_file = self.filename + '_decompressed.txt'

      elif self.data_type in ["graylevelimage", "colorimage"]:
         output_file = self.filename + '_decompressed.bmp'

      else:
         print("Unknown data type!")
         return None

      output_path = os.path.join(current_directory, output_file)

      # Read the compressed binary file
      with open(input_path, 'rb') as in_file:
         byte_data = in_file.read()

      # Convert the byte data to a binary string
      bit_string = StringIO()
      for byte in byte_data:
         bits = bin(byte)[2:].rjust(8, '0')
         bit_string.write(bits)
      bit_string = bit_string.getvalue()

      # Remove padding
      bit_string = self.remove_padding(bit_string)
      # Extract the code length info
      bit_string = self.extract_code_length_info(bit_string)
      # Convert the binary string to a list of integers
      encoded_text = self.binary_string_to_int_list(bit_string)
      # Decode the encoded text using the LZW decompression algorithm
      decompressed_text = self.decode(encoded_text)

      # Handle different data types

      if self.data_type == "text":
         with open(output_path, 'w') as out_file:
            out_file.write(decompressed_text)

      elif self.data_type == "graylevelimage":
         # Open the original image to get its dimensions
         orgImageFile = readPILimg(self.filename)  # Using your function
         nrows, ncols = orgImageFile.size[1], orgImageFile.size[0]

         # Convert characters back to integer values
         out = []
         for cc in decompressed_text:
            out.append(ord(cc))

         with open(output_path, 'w') as output:
            output.write(",".join(str(num) for num in out))

         # Ensure that the length matches the expected dimensions
         if len(out) != nrows * ncols:
            print("Error: Decompressed data size does not match image dimensions!")
            return None

         # Reshape the list into a 2D numpy array
         img_matrix = np.reshape(out, (nrows, ncols))
         restored_image = self.restore_original_image(img_matrix)

         # Convert to a grayscale image and save
         img = np2PIL(restored_image)
         img.show()
         img.save(output_path)

      elif self.data_type == "colorimage":
         # Open the original image to get its dimensions
         orgImageFile = readPILimg(self.filename)  # Using your function
         nrows, ncols = orgImageFile.size[1], orgImageFile.size[0]

         # Split decompressed text into RGB channels
         channel_size = nrows * ncols
         red_channel = decompressed_text[:channel_size]
         green_channel = decompressed_text[channel_size:2*channel_size]
         blue_channel = decompressed_text[2*channel_size:]

         # Convert back to integer arrays
         red_array = np.array([ord(c) for c in red_channel], dtype=np.uint8).reshape(nrows, ncols)
         green_array = np.array([ord(c) for c in green_channel], dtype=np.uint8).reshape(nrows, ncols)
         blue_array = np.array([ord(c) for c in blue_channel], dtype=np.uint8).reshape(nrows, ncols)

         # Restore original RGB image from difference images
         red_restored = self.restore_original_image(red_array)
         green_restored = self.restore_original_image(green_array)
         blue_restored = self.restore_original_image(blue_array)

         # Convert numpy arrays to PIL images before merging
         red_img = np2PIL(red_restored)
         green_img = np2PIL(green_restored)
         blue_img = np2PIL(blue_restored)

         # Merge RGB channels back into one image
         restored_image = merge_image(red_img, green_img, blue_img)

         # Save and show the restored image
         restored_image.save(f"{self.filename}_decompressed.bmp")
         restored_image.show()

      else:
         print("Unknown data type!")
         return None

      # Notify the user that decompression is complete
      print(f"{input_file} has been decompressed into {output_file}.")

      return output_path

   # A method to remove the padding info and the added zeros from the compressed
   # binary string and return the resulting string.
   def remove_padding(self, padded_encoded_data):
      # extract the padding info (the first 8 bits of the input string)
      padding_info = padded_encoded_data[:8]
      encoded_data = padded_encoded_data[8:]
      # remove the extra zeros (if any) and return the resulting string
      extra_padding = int(padding_info, 2) 
      if extra_padding != 0:
         encoded_data = encoded_data[:-1 * extra_padding]
      return encoded_data

   # A method to extract the code length info from the compressed binary string
   # and return the resulting string.
   # ---------------------------------------------------------------------------
   def extract_code_length_info(self, bitstring):
      # the first 8 bits of the input string contains the code length info
      codelength_info = bitstring[:8]
      self.codelength = int(codelength_info, 2)
      # return the resulting binary string after removing the code length info
      return bitstring[8:]

   # A method that converts the compressed binary string to a list of int codes
   # and returns the resulting list.
   # ---------------------------------------------------------------------------
   def binary_string_to_int_list(self, bitstring):
      # generate the list of integer codes from the binary string
      int_codes = []
      # for each compressed value (a binary string with codelength bits)
      for bits in range(0, len(bitstring), self.codelength):
         # compute the integer code and add it to the list
         int_code = int(bitstring[bits: bits + self.codelength], 2)
         int_codes.append(int_code)
      # return the resulting list
      return int_codes
   
   # A method that decodes a list of encoded integer values into a string (text) 
   # by using the LZW decompression algorithm and returns the resulting output.
   # ---------------------------------------------------------------------------
   def decode(self, encoded_values):
      # build the initial dictionary by mapping the index values in the extended 
      # ASCII table to their corresponding characters
      dict_size = 256
      dictionary = {i: chr(i) for i in range(dict_size)}

      # perform the LZW decompression algorithm
      # ------------------------------------------------------------------------
      from io import StringIO   # using StringIO for efficiency
      result = StringIO()
      # initialize w as the character corresponding to the first encoded value
      # in the list and add this character to the output string
      w = chr(encoded_values.pop(0))
      result.write(w)
      # iterate over each encoded value in the list
      for k in encoded_values:
         # if the value is in the dictionary
         if k in dictionary:
            # retrieve the corresponding string
            entry = dictionary[k]
         # if the value is equal to the current dictionary size
         elif k == dict_size:
            # construct the entry
            entry = w + w[0]   # a special case where the entry is formed
         # if k is invalid (not in the dictionary and not equal to dict_size)
         else:
            # raise an error
            raise ValueError('Bad compressed k: %s' % k)
         # add the entry to the output
         result.write(entry)
         # w + the first character of the entry is added to the dictionary 
         # as a new sequence
         dictionary[dict_size] = w + entry[0]
         dict_size += 1
         # update w to the current entry
         w = entry
      
      # return the resulting output (the decompressed string/text)
      return result.getvalue()
