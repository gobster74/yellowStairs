import numpy as np
import cv2
import pyOptris as optris
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk

# Global variables
frame_counter_1m = 0
frame_counter_640i = 0
display_rate = 27  # Target GUI refresh rate
skip_frames_1m = 1000 // display_rate  # Skips 37 frames for the 1M camera
skip_frames_640i = 32 // display_rate  # Skips ~1 frame for the 640i camera
running = True

# Initialize the cameras
def initialize_cameras():
    print("Initializing cameras...")
    xml_files = ["17092037.xml", "6060300.xml"]
    # Initialize PI 1M
    result = optris.multi_usb_init(xml_files[0], None, None)
    if result != 0:
        print(f"Failed to initialize PI 1M: {result}")
        return False
    # Initialize PI 640i
    result = optris.multi_usb_init(xml_files[1], None, None)
    if result != 0:
        print(f"Failed to initialize PI 640i: {result}")
        return False
    print("Cameras initialized successfully.")
    return True

# Close the camera safely
def close_camera():
    optris.terminate()
    print("Cameras terminated successfully.")

# Process the PI 1M camera feed
def process_pi_1m():
    global frame_counter_1m
    w, h = 72, 56  # Reduced frame size for PI 1M
    while running:
        if frame_counter_1m % skip_frames_1m == 0:  # Display every 37th frame
            frame = optris.get_palette_image(w, h)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            label_img_1m.imgtk = imgtk
            label_img_1m.configure(image=imgtk)
        frame_counter_1m += 1
        time.sleep(1 / display_rate)

# Process the PI 640i camera feed
def process_pi_640i():
    global frame_counter_640i 
    w, h = 642, 480  # Full frame size for PI 640i
    while running:
        if frame_counter_640i % skip_frames_640i == 0:  # Display based on 32Hz matching target refresh
            frame = optris.get_palette_image(w, h)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            label_img_640i.imgtk = imgtk
            label_img_640i.configure(image=imgtk)
        frame_counter_640i += 1
        time.sleep(1 / display_rate)

# Start the camera threads
def start_cameras():
    threading.Thread(target=process_pi_1m, daemon=True).start()
    threading.Thread(target=process_pi_640i, daemon=True).start()

# Create the GUI
def create_gui():
    global label_img_1m, label_img_640i

    window = tk.Tk()
    window.title("Thermal Camera Control")
    window.geometry("1600x600")  # Side-by-side layout for both cameras

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

# Main execution
if __name__ == "__main__":
    if not initialize_cameras():
        print("Camera initialization failed. Exiting...")
    else:
        start_cameras()
        create_gui()
