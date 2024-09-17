import numpy as np
import cv2
import pyOptris as optris
import time

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
if not initialize_camera('17092037f.xml'):
    print("Failed to initialize the camera after multiple attempts.")
    exit(1)

# Get image size
w, h = get_image_size()
if w == -1 or h == -1:
    print("Camera stream failed to start. Exiting.")
    optris.terminate()
    exit(1)

# Create a window for the live thermal feed
cv2.namedWindow('Thermal Live View', cv2.WINDOW_NORMAL)

def live_view(scale_factor=3):
    while True:
        try:
            # Capture the thermal image
            thermal_image = optris.get_thermal_image(w, h)[0]

            # Get the min and max values for dynamic scaling
            min_temp = np.min(thermal_image)
            max_temp = np.max(thermal_image)

            # If min and max are too close, adjust manually to avoid flat images
            if max_temp - min_temp < 1e-5:
                min_temp = min_temp - 1
                max_temp = max_temp + 1

            # Normalize the image based on the dynamic min and max values
            normalized_image = np.uint8(255 * (thermal_image - min_temp) / (max_temp - min_temp))

            # Apply a colormap to the normalized image
            color_image = cv2.applyColorMap(normalized_image, cv2.COLORMAP_JET)

            # Resize the image for better visualization
            resized_image = cv2.resize(color_image, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_LINEAR)

            # Display the live frame
            cv2.imshow('Thermal Live View', resized_image)

            # Press 'q' to quit the live view
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Error capturing frame: {e}")
            break

    # Release the camera and close windows
    optris.terminate()
    cv2.destroyAllWindows()

# Run the live view
live_view()
