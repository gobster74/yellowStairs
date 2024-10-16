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
running = True
active_camera = 'PI 1M'
switch_requested = False
frame_mode = 'full'  # Set to 'reduced' for initialization

# Camera frame configurations
camera_frames = {
    'PI 1M': {
        'reduced': {'xml_file': '17092037f.xml', 'size': (72, 56), 'min_temp': 600, 'max_temp': 1800, 'frequency': '1000Hz'},
        'full': {'xml_file': '17092037.xml', 'size': (764, 480), 'min_temp': 500, 'max_temp': 1800, 'frequency': '32Hz'}
    },
    'PI 640i': {
        'reduced': {'xml_file': '6060300f.xml', 'size': (642, 120), 'min_temp': 0, 'max_temp': 250, 'frequency': '125Hz'},
        'full': {'xml_file': '6060300.xml', 'size': (642, 480), 'min_temp': 0, 'max_temp': 250, 'frequency': '32Hz'}
    }
}

# Scaling factors for different cameras and frame modes
scale_factors = {'PI 1M': 1, 'PI 640i': 1}

def initialize_cameras():
    print("Initializing cameras...")
    
    xml_files = [
        camera_frames['PI 1M'][frame_mode]['xml_file'],
        camera_frames['PI 640i'][frame_mode]['xml_file']
    ]
    
    # Call the multi_usb_init function with the XML files
    result = optris.multi_usb_init(xml_files[0], None, None)  # Initialize the first camera
    if result != 0:
        print(f"Failed to initialize PI 1M: {result}")
        return False
    
    result = optris.multi_usb_init(xml_files[1], None, None)  # Initialize the second camera
    if result != 0:
        print(f"Failed to initialize PI 640i: {result}")
        return False
    
    print("Cameras initialized successfully.")
    return True

def close_camera():
    try:
        optris.terminate()
        print("Camera terminated successfully")
    except Exception as e:
        print(f"Failed to terminate camera: {e}")

def toggle_recording():
    global recording
    recording = not recording
    if recording:
        print(f"Recording started on {active_camera}")
    else:
        stop_recording()

def stop_recording():
    global frame_buffer, times_computer
    if frame_buffer:
        filename_prefix = f'frame_buffer_{active_camera}_{int(time.time())}'
        with open(f'{filename_prefix}.bin', 'wb') as f:
            np.save(f, np.array(frame_buffer))  # Save frame buffer as binary
        with open(f'{filename_prefix}_times.bin', 'wb') as f:
            np.save(f, np.array(times_computer))  # Save timestamps as binary
        print(f"Recording stopped and files saved: {filename_prefix}")
    else:
        print("No data to save")
    frame_buffer = []
    times_computer = []


def switch_frame():
    global frame_mode
    frame_mode = 'reduced' if frame_mode == 'full' else 'full'
    print(f"Switch requested to {frame_mode} frame")

def capture_camera_frames(camera_name):
    global frame_buffer, times_computer, running, switch_requested

    while running:
        frame_config = camera_frames[camera_name][frame_mode]
        w, h = frame_config['size']

        while running:
            try:
                thermal_image = optris.get_thermal_image(w, h)[0]
                print(f"Frame captured from {camera_name} ({frame_mode} frame).")

                min_temp = frame_config['min_temp']
                max_temp = frame_config['max_temp']
                normalized_image = np.uint8(255 * (thermal_image - min_temp) / (max_temp - min_temp))
                color_image = cv2.applyColorMap(normalized_image, cv2.COLORMAP_JET)

                scale_factor = scale_factors[camera_name]
                resized_image = cv2.resize(color_image, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_LINEAR)

                cv2.putText(resized_image, f"Camera: {camera_name} ({frame_mode} frame)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow(f'Thermal Live View - {camera_name}', resized_image)

                if recording:
                    frame_buffer.append(thermal_image)
                    times_computer.append(time.time())

                if switch_requested:
                    close_camera()
                    switch_requested = False
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'): 
                    break
                time.sleep(0.1)
            except Exception as e:
                print(f"Error capturing frame from {camera_name}: {e}")
                break

        close_camera()
        cv2.destroyAllWindows()

def start_both_cameras():
    for camera_name in ['PI 1M', 'PI 640i']:
        thread = threading.Thread(target=capture_camera_frames, args=(camera_name,))
        thread.start()

def create_gui():
    window = tk.Tk()
    window.title("Thermal Camera Control")
    window.geometry("400x250")

    record_button = tk.Button(window, text="Start/Stop Recording", command=toggle_recording)
    record_button.pack(pady=10)

    switch_frame_button = tk.Button(window, text="Switch Full/Reduced Frame", command=switch_frame)
    switch_frame_button.pack(pady=10)

    quit_button = tk.Button(window, text="Quit", command=lambda: on_closing(window))
    quit_button.pack(pady=10)

    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop() 

def on_closing(window):
    global running
    running = False  # Stop live view
    window.quit()
    window.destroy()

if __name__ == "__main__":
    if not initialize_cameras():  # Call it here without arguments
        print("Camera initialization failed. Exiting...")
    else:
        start_both_cameras()  # Start both cameras if initialization is successful
        create_gui()  # Start the GUI
