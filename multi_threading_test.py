import numpy as np
import cv2
import pyOptris as optris
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk
import ctypes
# Global variables
recording = False
frame_buffer_1m = []
frame_buffer_640i = []
times_computer_1m = []
times_computer_640i = []
running = True
frame_mode = 'full'  # for initialization

# Camera frame configuration, information is already inside of the xml file
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

    # Load XML file 
    xml_files = [
        camera_frames['PI 1M'][frame_mode],
        camera_frames['PI 640i'][frame_mode]
    ]

    # PI 1M
    err,ID1 = optris.multi_usb_init(xml_files[0],None, 'log_name')
    if err != 0:
        print(f"Failed to initialize PI 1M: {err}")
        return False, None, None, None, None
    print(f"PI 1M ID: {ID1} Serial: {optris.get_multi_get_serial(ID1)}")

    # PI 640i
    err,ID2 = optris.multi_usb_init(xml_files[1],None,'log_name')
    if err != 0:
        print(f"Failed to initialize PI 640i: {err}")
        return False, None, None, None, None
    print(f"PI 640i ID: {ID2} Serial: {optris.get_multi_get_serial(ID2)}")

    print("Cameras initialized successfully.")

    #dimesions for the GUI (test) 
    width_1m, height_1m = 764, 480
    width_640i, height_640i = 640, 480
 
    return True,ID1,ID2, width_1m + width_640i, max(height_1m, height_640i)

def close_camera():
    try:
        optris.terminate()
        print("Cameras terminated successfully")
    except Exception as e:
        print(f"Failed to terminate cameras: {e}")

def toggle_recording(camera):
    global recording
    recording = not recording
    if recording:
        print(f"Recording started on {camera}")
    else:
        stop_recording(camera)

def stop_recording(camera):
    global frame_buffer_1m, frame_buffer_640i, times_computer_1m, times_computer_640i
    if camera == 'PI 1M' and frame_buffer_1m:
        filename_prefix = f'frame_buffer_{camera}_{int(time.time())}'
        with open(f'{filename_prefix}.bin', 'wb') as f:
            np.save(f, np.array(frame_buffer_1m))  # Save frame buffer as binary
        with open(f'{filename_prefix}_times.bin', 'wb') as f:
            np.save(f, np.array(times_computer_1m))  # Save timestamps as binary
        print(f"Recording stopped and files saved for {camera}: {filename_prefix}")
        frame_buffer_1m = []
        times_computer_1m = []
    elif camera == 'PI 640i' and frame_buffer_640i:
        filename_prefix = f'frame_buffer_{camera}_{int(time.time())}'
        with open(f'{filename_prefix}.bin', 'wb') as f:
            np.save(f, np.array(frame_buffer_640i))  # Save frame buffer as binary
        with open(f'{filename_prefix}_times.bin', 'wb') as f:
            np.save(f, np.array(times_computer_640i))  # Save timestamps as binary
        print(f"Recording stopped and files saved for {camera}: {filename_prefix}")
        frame_buffer_640i = []
        times_computer_640i = []
    else:
        print(f"No data to save for {camera}")

def switch_frame():
    global frame_mode
    frame_mode = 'reduced' if frame_mode == 'full' else 'full'
    print(f"Switch requested to {frame_mode} frame")

def process_pi_1m(ID):
    global frame_buffer_1m, times_computer_1m, running

    try:
        w, h = 764, 480  # PI 1M resolution

        while running:
            thermal_image = optris.get_multi_thermal_image(ID,w, h)[0]

            temperatureData = (thermal_image - 1000.0) / 10.0

            normalized_image = cv2.normalize(temperatureData, None, 0, 255, cv2.NORM_MINMAX)
            color_image = cv2.applyColorMap(np.uint8(normalized_image), cv2.COLORMAP_JET)
            cv2.putText(color_image, f"Camera: PI 1M ({frame_mode} frame)", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

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

def process_pi_640i(ID):
    global frame_buffer_640i, times_computer_640i, running

    try:
        w, h = 640, 480  # PI 640i resolution

        while running:
            thermal_image = optris.get_multi_thermal_image(ID,w, h)[0]
            temperatureData = (thermal_image - 1000.0) / 10.0
            normalized_image = cv2.normalize(temperatureData, None, 0, 255, cv2.NORM_MINMAX)
            color_image = cv2.applyColorMap(np.uint8(normalized_image), cv2.COLORMAP_JET)
            cv2.putText(color_image, f"Camera: PI 640i ({frame_mode} frame)", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

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

def start_cameras(ID1,ID2):
    threading.Thread(target=process_pi_1m, daemon=True,args=(ID1,)).start()
    threading.Thread(target=process_pi_640i, daemon=True,args=(ID2,)).start()

def create_gui(total_width, total_height):
    global label_img_1m, label_img_640i

    window = tk.Tk()
    window.title("Thermal Camera Control")
    window.geometry(f"{total_width}x{total_height + 100}")  

    # Frame for camera display
    frame_display = tk.Frame(window)
    frame_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Label to display camera output for PI 1M
    label_img_1m = tk.Label(frame_display, width = total_width // 2, height = total_height)
    label_img_1m.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Label to display camera output for PI 640i
    label_img_640i = tk.Label(frame_display, width = total_width // 2, height = total_height)
    label_img_640i.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Controls at the bottom
    frame_controls = tk.Frame(window)
    frame_controls.pack(side=tk.BOTTOM, fill=tk.X)

    record_button_1m = tk.Button(frame_controls, text="Start/Stop Recording (PI 1M)",
                                  command=lambda: toggle_recording('PI 1M'))
    record_button_1m.pack(side=tk.LEFT, padx=5, pady=5)

    record_button_640i = tk.Button(frame_controls, text="Start/Stop Recording (PI 640i)",
                                    command=lambda: toggle_recording('PI 640i'))
    record_button_640i.pack(side=tk.LEFT, padx=5, pady=5)

    switch_frame_button = tk.Button(frame_controls, text="Switch Full/Reduced Frame", command=switch_frame)
    switch_frame_button.pack(side=tk.LEFT, padx=5, pady=5)

    quit_button = tk.Button(frame_controls, text="Quit", command=lambda: on_closing(window))
    quit_button.pack(side=tk.LEFT, padx=5, pady=5)

    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()

def on_closing(window):
    global running
    running = False  # Stop live view
    close_camera()
    window.quit()
    window.destroy()

if __name__ == "__main__":
    # Initialize both cameras using multi_usb_init
    success, ID1, ID2, total_width, total_height = initialize_cameras()
    if not success:
        print("Cameras failed to initialize...")
    else: 
        start_cameras(ID1, ID2)

        create_gui(total_width, total_height)