import numpy as np
import cv2
import pyOptris as optris
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk

# Global variables
recording = False
frame_buffer_1m = []
frame_buffer_640i = []
times_computer_1m = []
times_computer_640i = []
running = True
frame_mode = 'full'  # For initializationa

camera_frames = {
    'PI 1M': {
        'full': '17092037f.xml',
        'reduced': '17092037.xml'
    },
    'PI 640i': {
        'full': '6060300f.xml',
        'reduced': '6060300.xml'
    }
}

def initialize_cameras():
    print("Initializing cameras...")

    # Load XML file paths based on frame mode
    xml_files = [
        camera_frames['PI 1M'][frame_mode],
        camera_frames['PI 640i'][frame_mode]
    ]

    # Initialize PI 1M
    err,ID1 = optris.multi_usb_init(xml_files[0],None, 'log_name')
    if err != 0:
        print(f"Failed to initialize PI 1M: {err}")
        return False
    print(ID1)
    print(optris.get_multi_get_serial(ID1))
    # Initialize PI 640i
    err,ID2 = optris.multi_usb_init(xml_files[1],None,'log_name')
    if err != 0:
        print(f"Failed to initialize PI 640i: {err}")
        return False
    print(ID2)
    print(optris.get_multi_get_serial(ID2))

    print("Cameras initialized successfully.")
    return True,ID1,ID2


def close_camera():
    optris.terminate()
    print("Cameras terminated successfully.")

def process_pi_1m(ID):
    global running
    # Call the function to get the image size
    w, h, err = optris.get_multi_palette_image_size(ID)  
    if w == -1 or h == -1:
        print(f"Error getting image size for PI 1M: {err}")
        return

    while running:
        frame = optris.get_multi_palette_image(ID, w, h)[0]  # Get the RGB image
        # Update GUI
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        label_img_1m.imgtk = imgtk
        label_img_1m.configure(image=imgtk)
        time.sleep(0.1)

def process_pi_640i(ID):
    global running
    # Call the function to get the image size
    w, h, err = optris.get_multi_palette_image_size(ID)  
    if w == -1 or h == -1:
        print(f"Error getting image size for PI 640i: {err}")
        return

    while running:
        frame = optris.get_multi_palette_image(ID, w, h)[0]  # Get the RGB image
        # Update GUI
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        label_img_640i.imgtk = imgtk
        label_img_640i.configure(image=imgtk)
        time.sleep(0.1)

def start_cameras(ID1,ID2):
    threading.Thread(target=process_pi_1m, daemon=True,args=(ID1,)).start()
    threading.Thread(target=process_pi_640i, daemon=True,args=(ID2,)).start()

def create_gui():
    global label_img_1m, label_img_640i

    window = tk.Tk()
    window.title("Thermal Camera Control")
    window.geometry("1500x700")  # Adjusted for better layout

    # Frame for camera display
    frame_display = tk.Frame(window)
    frame_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Label to display camera output for PI 1M
    label_img_1m = tk.Label(frame_display)
    label_img_1m.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Label to display camera output for PI 640i
    label_img_640i = tk.Label(frame_display)
    label_img_640i.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    quit_button = tk.Button(window, text="Quit", command=window.quit)
    quit_button.pack(side=tk.BOTTOM, padx=5, pady=5)

    window.protocol("WM_DELETE_WINDOW", lambda: close_camera() or window.quit())
    window.mainloop()

if __name__ == "__main__":
    # Initialize both cameras using multi_usb_init
    err,ID1,ID2 = initialize_cameras()
    if not err:
        print("Camera initialization failed. Exiting...")
    else:
        # Start capturing frames from both cameras in separate threads
        start_cameras(ID1,ID2)
        create_gui()  # Start the GUI