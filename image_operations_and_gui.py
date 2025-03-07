from PIL import Image, ImageTk
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zlib
import math
from io import StringIO
from LZW import LZWCoding

# Global Variables
current_directory = os.path.dirname(os.path.realpath(__file__))
image_file_path = ''  # No default image
compressed_file_path = ''
compression_method = 'text'


# Function to start GUI
def start():
    global gui
    gui = tk.Tk()
    gui.title('Image & Text Compression GUI')
    gui['bg'] = 'SeaGreen1'

    # Create menu
    menubar = tk.Menu(gui)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label='Open File', command=select_file)
    file_menu.add_command(label='Exit', command=gui.quit)
    menubar.add_cascade(label='File', menu=file_menu)

    method_menu = tk.Menu(menubar, tearoff=0)
    method_menu.add_command(label='Text', command=lambda: set_compression_method('text'))
    method_menu.add_command(label='GrayLevel Image', command=lambda: set_compression_method('graylevelimage'))
    method_menu.add_command(label='Color Image', command=lambda: set_compression_method('colorimage'))
    menubar.add_cascade(label='Methods', menu=method_menu)
    gui.config(menu=menubar)

    frame = tk.Frame(gui, bg='DodgerBlue4')
    frame.grid(row=0, column=0, padx=15, pady=15)

    global gui_img_panel, decompressed_img_panel
    gui_img_panel = tk.Label(frame, text='Original Image', bg='white', width=50, height=15)
    gui_img_panel.grid(row=0, column=0, padx=20, pady=10)
    decompressed_img_panel = tk.Label(frame, text='Decompressed Image', bg='white', width=50, height=15)
    decompressed_img_panel.grid(row=0, column=1, padx=20, pady=10)

    btn_compress = tk.Button(frame, text='Compress', command=compress_file)
    btn_compress.grid(row=1, column=0, pady=5)

    btn_decompress = tk.Button(frame, text='Decompress', command=decompress_file)
    btn_decompress.grid(row=1, column=1, pady=5)

    global stats_label
    stats_label = tk.Label(frame,
                           text='Entropy:\nAverage Code Length:\nCompression Ratio:\nInput Image size:\nCompressed Image size:\nDifference:',
                           bg='DodgerBlue4', fg='white', justify='left')
    stats_label.grid(row=2, column=0, columnspan=2, pady=5)

    gui.mainloop()


def set_compression_method(method):
    global compression_method
    compression_method = method
    messagebox.showinfo('Method Set', f'Compression method set to {method}')


def select_file():
    global image_file_path
    file_path = filedialog.askopenfilename(initialdir=current_directory, title='Select a file', filetypes=[
        ('Image files', '*.bmp;*.png;*.jpg;*.jpeg'), ('Text files', '*.txt')])

    if file_path:
        image_file_path = file_path
        if file_path.endswith(('.bmp', '.png', '.jpg', '.jpeg')):
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            img = ImageTk.PhotoImage(img)
            gui_img_panel.config(image=img, text='')
            gui_img_panel.image = img
        else:
            gui_img_panel.config(text='Text File Selected')
    else:
        messagebox.showinfo('Warning', 'No file selected.')


def compress_file():
    global compressed_file_path
    if not image_file_path:
        messagebox.showerror('Error', 'No file selected to compress!')
        return

    lzw = LZWCoding(image_file_path, compression_method)
    compressed_file_path = lzw.compress_file()
    if compressed_file_path:
        messagebox.showinfo('Success', f'File compressed and saved as {compressed_file_path}')


def decompress_file():
    global compressed_file_path
    if not compressed_file_path:
        messagebox.showerror('Error', 'No compressed file available!')
        return

    lzw = LZWCoding(compressed_file_path, compression_method)
    decompressed_file_path = lzw.decompress_file()
    if decompressed_file_path:
        messagebox.showinfo('Success', f'File decompressed and saved as {decompressed_file_path}')


if __name__ == '__main__':
    start()
