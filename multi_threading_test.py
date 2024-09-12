import threading
import pyOptris as optris
import time
import numpy as np
import os

# Constants
COUNTER_FILE = 'counter.txt'

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

# Counter management functions
def read_counter():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as file:
            return int(file.read().strip())
    return 1  # Default to 1 if the file does not exist

def write_counter(value):
    with open(COUNTER_FILE, 'w') as file:
        file.write(str(value))

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

# Proceed with allocating buffer if valid image size is retrieved
frames_captured = 5000
frame_buffer = np.empty((frames_captured, h, w), dtype=np.float32)
times_computer = np.empty(frames_captured)

# Initialize counter
counter = read_counter()

# Capture frames function
def capture_frames():
    start_time = time.time()
    for ii in range(frames_captured):
        try:
            thermal_image = optris.get_thermal_image(w, h)[0]
            frame_buffer[ii] = thermal_image
            times_computer[ii] = time.time()
            
            # Print frame statistics for debugging
            if ii % 100 == 0:  # Print every 100 frames
                print(f"Frame {ii}: min={np.min(thermal_image)}, max={np.max(thermal_image)}, mean={np.mean(thermal_image)}")
        
        except Exception as e:
            print(f"Error capturing frame {ii}: {e}")
            break
    
    end_time = time.time()
    print(f"Capture complete. Recording Time: {end_time - start_time:.2f} s")
    save_data()

# Save the buffer data to files
def save_data():
    global counter
    np.save(f'frame_buffer_{counter}.npy', frame_buffer)
    np.save(f'times_computer_{counter}.npy', times_computer)
    print(f"Buffers saved to files with counter {counter}.")
    counter += 1
    write_counter(counter)

# Start capture thread
start_time = time.time()
capture_thread = threading.Thread(target=capture_frames)
capture_thread.start()

# Wait for thread to finish
capture_thread.join()

end_time = time.time()
recording_time = end_time - start_time
print(f"Total Recording Time: {recording_time:.2f} s")
optris.terminate()

# Mean frame time and frequency
print(f"Mean Time per frame: {recording_time / frames_captured:.4f} s")
print(f"Mean Frequency per frame: {frames_captured / recording_time:.2f} Hz")
