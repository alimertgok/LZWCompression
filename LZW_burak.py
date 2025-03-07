import os
from PIL import Image
import numpy as np


class LZW:                                                        #LZW class

    def __init__(self, path, codelength, dataType):

        self.path = path                                          #sructer varibles for object
        self.compressed = []
        self.decompressed = []
        self.codelength = codelength
        self.dataType = dataType



    def compress(self, uncompressed):  # returns a list
        """Compress a string to a list of output symbols."""

        # Build the dictionary.
        dict_size = 256
        dictionary = {chr(i): i for i in range(dict_size)}

        w = ""
        result = []
        for c in uncompressed:
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                # Add wc to the dictionary.
                dictionary[wc] = dict_size
                dict_size += 1
                w = c

        # Output the code for w.
        if w:
            result.append(dictionary[w])
        return result

    def get_compressed_data(self, path):  # returns string (bit string) from binary file
        with open(path, "rb") as file:
            bit_string = ""
            byte = file.read(1)
            while (len(byte) > 0):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
        return bit_string

    def decompress(self, compressed):  # takes the list (compressed) and returns the string (original text content)
        """Decompress a list of output ks to a string."""
        from io import StringIO
        #print("from decompressed: compressed data: ", compressed)
        # Build the dictionary.
        dict_size = 256
        dictionary = {i: chr(i) for i in range(dict_size)}
        # use StringIO, otherwise this becomes O(N^2)
        # due to string concatenation in a loop
        result = StringIO()
        w = chr(compressed.pop(0))
        result.write(w)
        for k in compressed:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + w[0]
            else:
                raise ValueError('Bad compressed k: %s' % k)
            result.write(entry)

            # Add w+entry[0] to the dictionary.
            dictionary[dict_size] = w + entry[0]
            dict_size += 1

            w = entry
        return result.getvalue()

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"

        padded_info = "{0:08b}".format(extra_padding)
        print("padded info: ", padded_info)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        if (len(padded_encoded_text) % 8 != 0):
            print("Encoded text not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i + 8]
            b.append(int(byte, 2))
        return b

    def int_array_to_binary_string(self, int_array):
        import math
        bitstr = ""
        bits = self.codelength
        for num in int_array:
            for n in range(bits):
                if num & (1 << (bits - 1 - n)):
                    bitstr += "1"
                else:
                    bitstr += "0"
        return (bitstr)


    def get_compressed_file(self):
        file_name, file_extension = os.path.splitext(self.path)
        output_path = file_name + ".bin"
        output_path_2 = file_name + "_out.txt"
        imagePath = self.path


        with open(self.path, 'r+') as file, open(output_path, 'wb') as output, open(output_path_2, 'w+') as file2:


            if self.dataType == "number":
                arr = []
                mystring = ""
                for line in file:
                    for x in line.split(","):
                        arr.append(int(x))
                        mystring += str(chr(int(x)))
                #print("input-numbers: ", arr)
                mytext = mystring

            elif self.dataType == "text":
                mytext = file.read()
                mytext = mytext.rstrip()
            elif self.dataType == "image":

                img = Image.open(imagePath)
                img.show()
                arr = np.array(img.convert("L"))  # converting gray level


                (nrows, ncols) = arr.shape

                print("nrows x ncols: ", (nrows, ncols))
                mystring = ""
                for i in range(nrows):
                    for j in range(ncols):
                        mystring += str(chr(arr[i][j]))
                #print("input numbers: ", arr)
                mytext = mystring

            elif self.dataType == "colorimage":

                img = Image.open(imagePath)
                img.show()
                arr = np.array(img.convert("RGB"))  # converting RGB
                (nrows, ncols, depth) = arr.shape  # depth is always 3 -> r, g, b

                print("nrows x ncols x depth: ", (nrows, ncols, depth))
                mystring = ""
                for i in range(nrows):
                    for j in range(ncols):
                        for k in range(depth):
                            mystring += str(chr(arr[i][j][k]))
                #print("input numbers: ", arr)
                mytext = mystring


            else:
                print("Unknown data type !!!")

            int_encoded = self.compress(mytext)
            file2.write(str(int_encoded))  # not so important
            encoded_text = self.int_array_to_binary_string(int_encoded)
            padded_encoded_text = self.pad_encoded_text(encoded_text)
            b = self.get_byte_array(padded_encoded_text)
            output.write(bytes(b))

        print("Compressed")
        file2.close()
        return output_path

    # decoder
    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-1 * extra_padding]
        int_codes = []
        for bits in range(0, len(encoded_text), self.codelength):
            int_codes.append(int(encoded_text[bits:bits + self.codelength], 2))
        return int_codes

    def decompress_file(self,input_path):  # will be used in main. WORK ON THIS. THIS IS THE MISSING PART. ZOOM KAYDINDA YAZIYO ORDAN BAKABİLİRSİN.
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + "_decompressed" + ".txt"



        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""

            byte = file.read(1)
            while (len(byte) > 0):
                int_byte = ord(byte)
                bits = ""
                for n in range(8):
                    if int_byte & (1 << (7 - n)):
                        bits += "1"
                    else:
                        bits += "0"

                #print("byte :", byte)
                bits = bin(int_byte)[2:].rjust(8, '0')  # just uncommented this and it worked !!!
                # bits = bin(byte)[:].rjust(8, '0')           # this was uncommented.
                bit_string += bits
                byte = file.read(1)

            encoded_text = self.remove_padding(bit_string)
            #print("decompressed_file - encoded integers", encoded_text)
            decompressed_text = self.decompress(encoded_text)

            #output.write(decompressed_text)  # bu commentliydi eskiden

            print("Decompressed")

            if self.dataType == "number":
                out = []
                for cc in decompressed_text:
                    out.append(ord(cc))
                print("decompressed data: ", out)
                output.write(",".join(str(num) for num in out))
            elif self.dataType == "text":
                output.write(decompressed_text)
            elif self.dataType == "image":
                myImageFile = Image.open(self.path)
                nrows = myImageFile.size[1]
                ncols = myImageFile.size[0]
                out = []
                for cc in decompressed_text:
                    out.append(ord(cc))
                #print("decompressed data: ", out)
                output.write(",".join(str(num) for num in out))
                print(len(out))

                my_matrix = np.reshape(out, (nrows,ncols))   # this may cause error when the codelength is not enough. Try increasing it.
                img = Image.fromarray(np.uint8(my_matrix))
                img.show()
                img.save("{}_decompressed.bmp".format(filename))

            elif self.dataType == "colorimage":
                myImageFile = Image.open(self.path)
                nrows = myImageFile.size[1]
                ncols = myImageFile.size[0]
                out = []
                for cc in decompressed_text:
                    out.append(ord(cc))
                #print("decompressed data: ", out)
                output.write(",".join(str(num) for num in out))
                print(len(out))

                my_matrix = np.reshape(out, (nrows, ncols, 3))  # this may cause error when the codelength is not enough. Try increasing it.
                img = Image.fromarray(np.uint8(my_matrix))
                # img = Image.fromarray(my_matrix)
                img.show()
                img.save("{}_decompressed.bmp".format(filename))

            else:
                print("Unknown data type !!!")
            #output.write(out)

            return output_path
