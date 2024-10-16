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

# Initialize cameras
def initialize_cameras():
    xml_files = ["17092037.xml", "6060300.xml"]
    print("Initializing cameras...")
    # Initialize both cameras
    result = optris.multi_usb_init(xml_files[0], xml_files[1], None)
    if result != 0:
        print("Failed to initialize cameras.")
        return False
    print("Cameras initialized successfully.")
    return True

def close_camera():
    optris.terminate()
    print("Cameras terminated successfully.")

def process_pi_1m():
    global frame_buffer_1m, times_computer_1m, running

    try:
        w, h = 72, 56  # Adjust according to the PI 1M specs

        while running:
            thermal_image = optris.get_thermal_image(w, h)[0]
            normalized_image = cv2.normalize(thermal_image, None, 0, 255, cv2.NORM_MINMAX)
            color_image = cv2.applyColorMap(np.uint8(normalized_image), cv2.COLORMAP_JET)
            cv2.putText(color_image, "Camera: PI 1M", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Convert to a format suitable for Tkinter
            img = Image.fromarray(color_image)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the Tkinter label with the new image
            label_img_1m.imgtk = imgtk
            label_img_1m.configure(image=imgtk)

            if recording:
                frame_buffer_1m.append(thermal_image)
                times_computer_1m.append(time.time())

            time.sleep(0.1)

    except Exception as e:
        print(f"Error capturing frame from PI 1M: {e}")

def process_pi_640i():
    global frame_buffer_640i, times_computer_640i, running

    try:
        w, h = 764, 480  # Adjust according to the PI 640i specs

        while running:
            thermal_image = optris.get_thermal_image(w, h)[0]
            normalized_image = cv2.normalize(thermal_image, None, 0, 255, cv2.NORM_MINMAX)
            color_image = cv2.applyColorMap(np.uint8(normalized_image), cv2.COLORMAP_JET)
            cv2.putText(color_image, "Camera: PI 640i", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Convert to a format suitable for Tkinter
            img = Image.fromarray(color_image)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the Tkinter label with the new image
            label_img_640i.imgtk = imgtk
            label_img_640i.configure(image=imgtk)

            if recording:
                frame_buffer_640i.append(thermal_image)
                times_computer_640i.append(time.time())

            time.sleep(0.1)

    except Exception as e:
        print(f"Error capturing frame from PI 640i: {e}")

def start_cameras():
    threading.Thread(target=process_pi_1m, daemon=True).start()
    threading.Thread(target=process_pi_640i, daemon=True).start()

def create_gui():
    global label_img_1m, label_img_640i

    window = tk.Tk()
    window.title("Thermal Camera Control")
    window.geometry("800x600")  # Adjusted for better layout

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
