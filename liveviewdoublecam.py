import threading
import pyOptris as optris
import time
import numpy as np
import cv2
import tkinter as tk
from tkinter import messagebox

# Global variables
recording = False
frame_buffer = []
times_computer = []
running = True  # Control the live view loop
current_camera = None
camera_config = {
    "PI 1M": "17092037f.xml",
    "PI 640i": "6060300.xml" 
}

# Initialize the camera
def initialize_camera(camera_name, retries=3, delay=2):
    global current_camera
    serial_file = camera_config.get(camera_name)
    if not serial_file:
        print(f"Camera configuration for {camera_name} not found.")
        return False
    
    for attempt in range(retries):
        try:
            optris.usb_init(serial_file)
            current_camera = camera_name
            print(f"{camera_name} initialized successfully")
            return True
        except Exception as e:
            print(f"Initialization attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(delay)
    return False

# Retry getting image size
def get_image_size():
    try:
        w, h = optris.get_thermal_image_size()
        if w <= 0 or h <= 0:
            raise ValueError("Invalid image dimensions returned.")
        return w, h
    except Exception as e:
        print(f"Failed to get image size: {e}")
        return -1, -1

# Start or stop recording
def toggle_recording():
    global recording
    recording = not recording
    if recording:
        start_recording()
    else:
        stop_recording()

# Start recording
def start_recording():
    global frame_buffer, times_computer
    frame_buffer = []
    times_computer = []
    print("Recording started")

# Stop recording and save data
def stop_recording():
    global frame_buffer, times_computer
    if frame_buffer:
        np.save(f'frame_buffer_{int(time.time())}.npy', np.array(frame_buffer))
        np.save(f'times_computer_{int(time.time())}.npy', np.array(times_computer))
        print("Recording stopped and files saved")
    else:
        print("No data to save")

# Switch camera
def switch_camera(camera_name):
    global current_camera, w, h
    if current_camera == camera_name:
        print(f"Already using {camera_name}")
        return
    if initialize_camera(camera_name):
        w, h = get_image_size()
        if w == -1 or h == -1:
            print(f"Failed to get image size for {camera_name}.")
            return
        print(f"Switched to {camera_name}")

# GUI
def create_gui():
    window = tk.Tk()
    window.title("Thermal Camera Control")
    window.geometry("400x150")

    tk.Button(window, text="Start/Stop Recording", command=toggle_recording).pack(pady=10)
    tk.Button(window, text="Switch to PI 1M", command=lambda: switch_camera("PI 1M")).pack(pady=5)
    tk.Button(window, text="Switch to PI 640i", command=lambda: switch_camera("PI 640i")).pack(pady=5)

    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()

# Window closing
def on_closing(window):
    global running
    if recording:
        stop_recording()
    running = False  # Stop the live view loop
    optris.terminate()
    cv2.destroyAllWindows()
    window.quit()
    window.destroy()

# Function to continuously capture and display frames
def live_view():
    scale_factor = 8  # change to get a bigger screen
    global recording, frame_buffer, times_computer, running, current_camera

    while running:
        try:
            if current_camera is None:
                print("No camera initialized.")
                time.sleep(1)
                continue

            # Capture the thermal image
            thermal_image = optris.get_thermal_image(w, h)[0]

            # Convert the image to an 8-bit format for OpenCV display
            normalized_image = cv2.normalize(thermal_image, None, 0, 255, cv2.NORM_MINMAX)
            display_image = np.uint8(normalized_image)

            # Resize the image for larger display
            resized_image = cv2.resize(display_image, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_LINEAR)

            # Display the frame
            cv2.imshow('Live Thermal View', resized_image)

            # Record frames if recording is active
            if recording:
                frame_buffer.append(thermal_image)
                times_computer.append(time.time())

            # Input to close the window
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
                break
        except Exception as e:
            print(f"Error during live view: {e}")
            break

    # Clean up
    cv2.destroyAllWindows()

# Start the GUI in a separate thread
gui_thread = threading.Thread(target=create_gui)
gui_thread.start()

# Start the live view
live_view()
