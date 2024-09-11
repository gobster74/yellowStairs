import threading
import pyOptris as optris
import time as time
import cv2
import numpy as np
import matplotlib.pyplot as plt

# USB connection initialization
optris.usb_init('17092037f.xml')

w, h = optris.get_thermal_image_size()
pw, ph = optris.get_palette_image_size()
print('{} x {}'.format(w, h))

frames_captured = 5000
frame_buffer = np.empty((frames_captured, h, w))
times_computer = np.empty(frames_captured)

# This function will run in a separate thread, continuously capturing frames
def capture_frames():
    for ii in range(frames_captured):
        frame_buffer[ii] = optris.get_thermal_image(w, h)
        times_computer[ii] = time.time()

start_time = time.time()

# Start the capture thread
capture_thread = threading.Thread(target=capture_frames)
capture_thread.start()

# Wait for the capture thread to finish
capture_thread.join()

end_time = time.time()

recording_time = end_time - start_time
print("Recording Time is {:.2f} s".format(recording_time))
optris.terminate()

# Optionally, plot the timing data
# plt.figure()
# plt.plot(times_computer - times_computer[0])
# plt.plot(np.linspace(0, recording_time, frames_captured))
# plt.show()

print("Mean Time per frame is {:.4f} s".format(recording_time / frames_captured))
print("Mean Freq per frame is {:.2f} Hz".format(frames_captured / recording_time))