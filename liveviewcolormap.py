import numpy as np
import cv2
import pyOptris as optris
import time
import threading
import tkinter as tk

# Global variables
recording = False
frame_buffer = []
times_computer = []
full_frame = True  # Switch between full and reduced frame
running = True
scale_factor = 6

# Initialize the camera
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
if not initialize_camera('17092037.xml'):
    print("Failed to initialize the camera after multiple attempts.")
    exit(1)

# Get image size
w, h = get_image_size()
if w == -1 or h == -1:
    print("Camera stream failed to start. Exiting.")
    optris.terminate()
    exit(1)

# Start or stop recording
def toggle_recording():
    global recording
    recording = not recording
    if recording:
        print("Recording started")
    else:
        stop_recording()

# Stop recording and save the frame buffer
def stop_recording():
    global frame_buffer, times_computer
    if frame_buffer:
        np.save(f'frame_buffer_{int(time.time())}.npy', np.array(frame_buffer))
        np.save(f'times_computer_{int(time.time())}.npy', np.array(times_computer))
        print("Recording stopped and files saved")
    else:
        print("No data to save")
    frame_buffer = []
    times_computer = []

# Switch between full and reduced frame
def toggle_frame_size():
    global full_frame
    full_frame = not full_frame
    if full_frame:
        print("Switched to full frame")
    else:
        print("Switched to reduced frame")

# Function to display live thermal view
def live_view(scale_factor=6):
    global frame_buffer, times_computer, running

    while running:
        try:
            # Capture the thermal image
            if full_frame:
                thermal_image = optris.get_thermal_image(w, h)[0]
            else:
                thermal_image = optris.get_thermal_image(w//2, h//2)[0]  # Reduced frame

            # Normalize the image
            min_temp = np.min(thermal_image)
            max_temp = np.max(thermal_image)
            normalized_image = np.uint8(255 * (thermal_image - min_temp) / (max_temp - min_temp))

            # Apply a colormap
            color_image = cv2.applyColorMap(normalized_image, cv2.COLORMAP_JET)

            # Resize the image
            resized_image = cv2.resize(color_image, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_LINEAR)

            # Display the live frame
            cv2.imshow('Thermal Live View', resized_image)

            # Record frames if recording is active
            if recording:
                frame_buffer.append(thermal_image)
                times_computer.append(time.time())

            # Press 'q' to quit the live view
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Error capturing frame: {e}")
            break

    # Clean up when done
    if recording:
        stop_recording()
    optris.terminate()
    cv2.destroyAllWindows()

# Create the GUI for buttons
def create_gui():
    window = tk.Tk()
    window.title("Thermal Camera Control")
    window.geometry("400x150")

    # Start/Stop recording button
    record_button = tk.Button(window, text="Start/Stop Recording", command=toggle_recording)
    record_button.pack(pady=20)

    # Full/Reduced frame switch button
    frame_button = tk.Button(window, text="Switch Full/Reduced Frame", command=toggle_frame_size)
    frame_button.pack(pady=20)

    # Quit button
    quit_button = tk.Button(window, text="Quit", command=lambda: on_closing(window))
    quit_button.pack(pady=20)

    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()

# Graceful closing of the app
def on_closing(window):
    global running
    running = False  # Stop live view
    window.quit()
    window.destroy()

# Run live view in a separate thread
def run_live_view():
    live_view(scale_factor=3)

# Start GUI in a separate thread
gui_thread = threading.Thread(target=create_gui)
gui_thread.start()

# Start live view in the main thread
run_live_view()
