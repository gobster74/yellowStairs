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

# Retry initialization function
def initialize_camera(serial_file, retries=3, delay=2):
    for attempt in range(retries):
        try:
            optris.usb_init(serial_file)
            print("Camera initialized successfully")
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

# Initialize the camera with retries
if not initialize_camera('17092037f.xml'):
    print("Failed to initialize the camera after multiple attempts.")
    exit(1)

# Get image size and check for valid dimensions
w, h = get_image_size()
if w == -1 or h == -1:
    print("Camera stream failed to start. Exiting.")
    optris.terminate()
    exit(1)

# Function to start/stop recording
def toggle_recording():
    global recording
    recording = not recording
    if recording:
        start_recording()
    else:
        stop_recording()

# Function to start recording
def start_recording():
    global frame_buffer, times_computer
    frame_buffer = []
    times_computer = []
    print("Recording started")

# Function to stop recording and save data
def stop_recording():
    global frame_buffer, times_computer
    if frame_buffer:
        np.save(f'frame_buffer_{int(time.time())}.npy', np.array(frame_buffer))
        np.save(f'times_computer_{int(time.time())}.npy', np.array(times_computer))
        print("Recording stopped and files saved")
    else:
        print("No data to save")

# creates GUI
def create_gui():
    window = tk.Tk()
    window.title("Thermal Camera Control")
    window.geometry("300x100")
    
    start_button = tk.Button(window, text="Start/Stop Recording", command=toggle_recording)
    start_button.pack(pady=20)
    
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()

# window closing
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
    global recording, frame_buffer, times_computer, running

    while running:
        try:
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

            #input to close the window
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
