import os.path
import tkinter as tk

import numpy as np
from PIL import ImageTk, Image
from tkinter import filedialog
import image_tools
from LZW import LZWCoding

# def openFile():
#     global originalFilePath
#     originalFilePath = filedialog.askopenfilename(initialdir=os.path.curdir, title="select a file", filetypes=(
#     ("bmp files", "*.bmp"),("text files", "*.txt"), ("all files", "*.*")))  # now, selected file's name is in filename:str

def compressGrayLevelImageFile():

    lzw = LZWCoding("MEF_logo.bmp", "graylevelimage")
    lzw.compress_file()
    lzw.decompress_file()


def compare_images(original_path, decompressed_path):
    """Compare the original and decompressed image using custom image library."""

    # Load images
    original_img = image_tools.readPILimg(original_path).convert("L")  # Convert to grayscale
    decompressed_img = image_tools.readPILimg(decompressed_path).convert("L")  # Convert to grayscale

    # Convert to numpy arrays
    original_array = image_tools.PIL2np(original_img)
    decompressed_array = image_tools.PIL2np(decompressed_img)

    # Print shape comparison
    print(f"Original Image Shape: {original_array.shape}")
    print(f"Decompressed Image Shape: {decompressed_array.shape}")

    # Check if dimensions match
    if original_array.shape != decompressed_array.shape:
        print("❌ ERROR: Image dimensions do not match!")
        return

    # Compute absolute difference
    difference = np.abs(original_array - decompressed_array)

    # Mean Squared Error (MSE)
    mse = np.mean(difference ** 2)
    print(f"📏 Mean Squared Error (MSE): {mse:.4f}")

    # Save difference image
    diff_path = "difference.png"
    image_tools.np2PIL(difference).save(diff_path)
    print(f"⚠️ Difference image saved as: {diff_path}")


if __name__ == "__main__":
    compressGrayLevelImageFile()
