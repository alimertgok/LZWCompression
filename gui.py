from PIL import Image, ImageTk
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zlib
import math
from io import StringIO
from LZW import LZWCoding  # Importing the backend class

# Global Variables
current_directory = os.path.dirname(os.path.realpath(__file__))
image_file_path = ''  # No default image
compressed_file_path = ''
decompressed_file_path = ''
compression_method = 'text'


def start():
    global gui
    gui = tk.Tk()
    gui.title('Image & Text Compression GUI')
    gui['bg'] = 'SeaGreen1'
    gui.geometry("800x500")  # Başlangıç pencere boyutu
    gui.minsize(800, 500)  # Minimum boyut belirle

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

    # Make the layout responsive
    gui.columnconfigure(0, weight=1)
    gui.rowconfigure(0, weight=1)

    frame = tk.Frame(gui, bg='DodgerBlue4')
    frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(2, weight=1)
    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=0)
    frame.rowconfigure(2, weight=0)

    # Original Image Panel
    global gui_img_panel
    gui_img_panel = tk.Label(frame, text='Original Image', bg='white', width=50, height=20)
    gui_img_panel.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

    # Compress & Decompress Buttons
    btn_compress = tk.Button(frame, text='Compress', command=compress_file)
    btn_compress.grid(row=1, column=0, pady=5, sticky="ew")

    btn_decompress = tk.Button(frame, text='Decompress', command=decompress_file)
    btn_decompress.grid(row=2, column=0, pady=5, sticky="ew")

    # Reset Button
    btn_reset = tk.Button(frame, text='Reset', command=reset_gui)
    btn_reset.grid(row=3, column=0, pady=5, sticky="ew")

    # Compressed File Label
    global compressed_file_label
    compressed_file_label = tk.Label(frame, text='Compressed File (.bin)', bg='white', width=50, height=5)
    compressed_file_label.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

    # Decompressed Image Panel
    global decompressed_img_panel
    decompressed_img_panel = tk.Label(frame, text='Decompressed Image', bg='white', width=50, height=20)
    decompressed_img_panel.grid(row=0, column=2, padx=20, pady=10, sticky="nsew")

    # Statistics Labels
    global stats_label
    stats_label = tk.Label(frame,
                           text='Entropy:\nAverage Code Length:\nCompression Ratio:\nInput Image size:\nCompressed Image size:\nDifference:',
                           bg='DodgerBlue4', fg='white', justify='left')
    stats_label.grid(row=2, column=2, pady=5, sticky="ew")

    gui.mainloop()


def update_stats(entropy, avg_code_length, compression_ratio, input_size, compressed_size, difference, data_type):
    try:
        if data_type == "text":
            entropy_display = "N/A"  # Text dosyaları için entropy hesaplanmaz
        else:
            entropy = float(entropy)
            entropy_display = f"{entropy:.2f} bits/pixel"

        avg_code_length = int(avg_code_length)
        compression_ratio = float(compression_ratio)
        input_size = int(input_size)
        compressed_size = int(compressed_size)
        difference = int(difference)

        stats_label.config(text=f"Entropy: {entropy_display}\n"
                                f"Average Code Length: {avg_code_length} bits\n"
                                f"Compression Ratio: {compression_ratio:.2f}x\n"
                                f"Input Image Size: {input_size:,d} bytes ({input_size / 1024:.2f} KB)\n"
                                f"Compressed Image Size: {compressed_size:,d} bytes ({compressed_size / 1024:.2f} KB)\n"
                                f"Difference: {difference:,d} bytes ({difference / 1024:.2f} KB)")
    except Exception as e:
        messagebox.showerror('Error', f"Stats Update Error: {str(e)}")



def reset_gui():
    global image_file_path, compressed_file_path, decompressed_file_path
    image_file_path = ''
    compressed_file_path = ''
    decompressed_file_path = ''
    gui_img_panel.config(image='', text='Original Image', width=50, height=20)
    decompressed_img_panel.config(image='', text='Decompressed Image', width=50, height=20)
    compressed_file_label.config(text='Compressed File (.bin)')
    stats_label.config(text='Entropy:\nAverage Code Length:\nCompression Ratio:\nInput Image size:\nCompressed Image size:\nDifference:')

def set_compression_method(method):
    global compression_method
    compression_method = method
    messagebox.showinfo('Method Set', f'Compression method set to {method}')


def select_file():
    global image_file_path
    file_path = filedialog.askopenfilename(
        initialdir=current_directory,
        title='Select a file',
        filetypes=[('All Supported Files', '*.bmp;*.png;*.jpg;*.jpeg;*.txt'),  # Tüm desteklenen formatlar
                   ('Image Files', '*.bmp;*.png;*.jpg;*.jpeg'),  # Görüntü dosyaları
                   ('Text Files', '*.txt')]  # TXT dosyaları
    )

    if file_path:
        image_file_path = file_path
        if file_path.endswith(('.bmp', '.png', '.jpg', '.jpeg')):
            img = Image.open(file_path)
            img.thumbnail((300, 300))
            img = ImageTk.PhotoImage(img)
            gui_img_panel.config(image=img, text='', width=300, height=300)
            gui_img_panel.image = img
        elif file_path.endswith('.txt'):
            gui_img_panel.config(text=f'Text File Selected: {os.path.basename(file_path)}', image='')

    else:
        messagebox.showinfo('Warning', 'No file selected.')



def compress_file():
    global compressed_file_path
    if not image_file_path:
        messagebox.showerror('Error', 'No file selected to compress!')
        return

    # Eğer dosya zaten ".txt" uzantılıysa, tekrar ekleme
    input_path = image_file_path
    if compression_method == "text" and not image_file_path.endswith(".txt"):
        input_path += ".txt"

    lzw = LZWCoding(input_path, compression_method)
    try:
        compressed_file_path = lzw.compress_file()

        if not compressed_file_path.endswith(".bin"):
            compressed_file_path += ".bin"

        compressed_file_label.config(text=f'Compressed File: {os.path.basename(compressed_file_path)}')

        update_stats(lzw.entropy, lzw.avg_code_length, lzw.compression_ratio,
                     lzw.input_size, lzw.compressed_size, lzw.difference, lzw.data_type)

        messagebox.showinfo('Success', f'File compressed and saved as {compressed_file_path}')
    except Exception as e:
        messagebox.showerror('Error', f'Compression Error: {str(e)}')




def decompress_file():
    global compressed_file_path, decompressed_file_path
    if not compressed_file_path:
        messagebox.showerror('Error', 'No compressed file available!')
        return

    lzw = LZWCoding(compressed_file_path, compression_method)
    try:
        decompressed_file_path = lzw.decompress_file()
        if decompressed_file_path and os.path.exists(decompressed_file_path):
            messagebox.showinfo('Success', f'File decompressed and saved as {decompressed_file_path}')

            # Eğer dosya bir TEXT ise, GUI'de sadece metin olarak göster
            if decompressed_file_path.endswith(".txt"):
                decompressed_img_panel.config(text=f"Decompressed Text File:\n{os.path.basename(decompressed_file_path)}", image='')
                return  # Görüntü açmayı denememesi için burada çık

            # Eğer dosya bir GÖRÜNTÜ ise, Tkinter'da göster
            if decompressed_file_path.endswith(('.bmp', '.png', '.jpg', '.jpeg')):
                img = Image.open(decompressed_file_path)
                img.thumbnail((300, 300))
                img = ImageTk.PhotoImage(img)
                decompressed_img_panel.config(image=img, text='')
                decompressed_img_panel.image = img
        else:
            messagebox.showerror('Error', 'Decompression failed! File not created.')
    except Exception as e:
        messagebox.showerror('Error', f'Decompression Error: {str(e)}')



if __name__ == '__main__':
    start()