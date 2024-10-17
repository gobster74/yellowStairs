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

# Initialize cameras
def initialize_cameras():
    print("Initializing cameras...")
    # Ensure to load the camera XML configuration properly
    result = optris.usb_init("6060300f.xml")
    if result != 0:
        print("Failed to initialize cameras.")
        return False
    print("Cameras initialized successfully.")
    return True

def close_camera():
    optris.terminate()
    print("Cameras terminated successfully.")

def process_pi_1m():
    global running
    w, h = optris.get_palette_image_size()  # Get image size
    while running:
        frame = optris.get_palette_image(w, h)  # Get the RGB image
        # Update GUI
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        label_img_1m.imgtk = imgtk
        label_img_1m.configure(image=imgtk)
        time.sleep(0.1)

def process_pi_640i():
    global running
    w, h = optris.get_palette_image_size()  # Get image size
    while running:
        frame = optris.get_palette_image(w, h)  # Get the RGB image
        # Update GUI
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        label_img_640i.imgtk = imgtk
        label_img_640i.configure(image=imgtk)
        time.sleep(0.1)

def start_cameras():
    threading.Thread(target=process_pi_1m, daemon=True).start()
    threading.Thread(target=process_pi_640i, daemon=True).start()

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
    if not initialize_cameras():
        print("Camera initialization failed. Exiting...")
    else:
        start_cameras()
        create_gui()  # Start the GUI
