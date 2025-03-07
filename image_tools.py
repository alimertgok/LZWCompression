from PIL import Image
import numpy as np


def readPILimg(image):
    img = Image.open(image)
    return img


def red_values(img):
    red = list(img.getdata(0))  # Directly access the opened image
    return red


def green_values(img):
    green = list(img.getdata(1))  # Directly access the opened image
    return green


def blue_values(img):
    blue = list(img.getdata(2))  # Directly access the opened image
    return blue


def merge_image(r, g, b):
    return Image.merge("RGB", (r, g, b))


def color2gray(img):
    img_gray = img.convert('L')
    return img_gray


def PIL2np(img):
    imgarray = np.array(img)
    return imgarray


def np2PIL(image):
    img = Image.fromarray(np.uint8(image))
    return img


def arr_to_PIL(arr):
    return Image.fromarray(arr)


if __name__ == "__main__":
    img = readPILimg("test_image.jpg")  # Open the image once
    red = red_values(img)  # Pass the already opened image
    green = green_values(img)  # Pass the already opened image
    blue = blue_values(img)  # Pass the already opened image
    gray = color2gray(img)








