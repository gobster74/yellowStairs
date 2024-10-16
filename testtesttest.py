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
toggled = False  # To track whether reduced mode is active
crop_size = 100  # Size of the crop area (width and height)

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
        img = Image.fromarray(frame)
        
        # Update GUI
        imgtk = ImageTk.PhotoImage(image=img)
        label_img_1m.imgtk = imgtk
        label_img_1m.configure(image=imgtk)
        time.sleep(0.1)

def process_pi_640i():
    global running, toggled

    w, h = optris.get_palette_image_size()  # Get image size
    while running:
        frame = optris.get_palette_image(w, h)  # Get the RGB image

        # If reduced mode is active, crop the area around the clicked point
        if toggled:
            # Calculate cropping area based on the click position
            start_x = click_x - crop_size // 2
            start_y = click_y - crop_size // 2
            end_x = click_x + crop_size // 2
            end_y = click_y + crop_size // 2

            # Ensure the cropping area is within bounds
            start_x = max(0, start_x)
            start_y = max(0, start_y)
            end_x = min(w, end_x)
            end_y = min(h, end_y)

            # Ensure the cropping area is valid
            if start_x < end_x and start_y < end_y:
                cropped_frame = frame[start_y:end_y, start_x:end_x]
                zoomed_img = cv2.resize(cropped_frame, (w, h))
                img = Image.fromarray(zoomed_img)
            else:
                print("Invalid cropping area.")  # Debugging line for invalid area
        else:
            img = Image.fromarray(frame)

        # Update GUI
        imgtk = ImageTk.PhotoImage(image=img)
        label_img_640i.imgtk = imgtk
        label_img_640i.configure(image=imgtk)

        time.sleep(0.1)

def toggle_frame_mode(event):
    global toggled

    # Toggle the reduced frame mode
    toggled = not toggled

    if toggled:
        print("Switched to reduced frame mode.")
    else:
        print("Switched to full frame mode.")

def capture_click(event):
    global click_x, click_y

    # Capture the click coordinates
    click_x, click_y = event.x, event.y
    print(f"Click coordinates: ({click_x}, {click_y})")

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

    # Bind the right mouse button click to toggle the frame mode
    label_img_640i.bind("<Button-3>", toggle_frame_mode)
    # Bind left mouse button click to capture click coordinates
    label_img_640i.bind("<Button-1>", capture_click)

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
