import os.path
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import filedialog
from LZW import LZW


def compressGrayImage():                                # This function creates a object with path that we gave and makes GRAY compression.
    photo = LZW(ourFilePath, 20, "image")
    newpath = photo.get_compressed_file()             # 'write_compressed_file' function returns changed new path
    photo.decompress_file(newpath)                      # decompression calling with new path


def compressColorImage():                               #This function creates a object with path that we gave and makes COLOR compression.
    photo = LZW(ourFilePath, 20, "colorimage")
    newpath = photo.get_compressed_file()             # 'write_compressed_file' function returns changed new path
    photo.decompress_file(newpath)                      # decompression calling with new path

def SelectFile():
    global ourFilePath
    ourFilePath = filedialog.askopenfilename(initialdir=os.path.curdir,           #Creates file selection starting current dictionary that our programs location
    title="select a file", filetypes=(("bmp files", ".bmp"), ("all files", ".*")))

    return ourFilePath




root = tk.Tk()                                                                  #creates our gui
root.title("LZW Compression")                                                   #gives title
root.geometry("800x200")                                                        #gui size

leftFrame = tk.Frame(root, width=20, height=50)                                 #creates left frame
leftFrame.pack(side="left", padx=5)                                           #positioning our frame

rightFrame = tk.Frame(root, width=20, height=50)                                #creates right frame
rightFrame.pack(side="right", padx=5)                                         #positioning our frame

ourFilePath = SelectFile()                                                      #varible for path that we will use


fileSelectButton = tk.Button(root, text="Select a file", command=SelectFile)    #object creation for select button
fileSelectButton.pack(pady=5,)                                                  #positioning our button


leftButton = tk.Button(leftFrame, bg='blue',text="Compress and decompress Color image file", command=compressColorImage)      #object creation for color button
leftButton.pack(side="top")                                                                                         #positioning our button

rightButton = tk.Button(rightFrame,bg='red', text="Compress and decompress Gray level image file", command=compressGrayImage) #object creation for color button
rightButton.pack(side="top")                                                                                        #positioning our button


root.mainloop()                                                                  #makes our gui open
