import threading
import pyOptris as optris
import time as time
import cv2
import numpy as np
import matplotlib.pyplot as plt
# USB connection initialisation
optris.usb_init('17092037f.xml')

w, h = optris.get_thermal_image_size()
pw, ph = optris.get_palette_image_size()
print('{} x {}'.format(w, h))

# This function will run in a separate thread, continuously capturing frames
def capture_frames():
    for ii in range(5000):
        optris.get_thermal_image(w, h)
wp, hp = optris.get_palette_image_size()

frames_captured = 5000

frame_buffer = np.empty((72,56,4*1000))
times_computer =  np.empty((1000))


start_Time = time.time()

# Start the capture thread
capture_thread = threading.Thread(target=capture_frames)
capture_thread.start()

 
    
end_time = time.time()


recording_time = end_time-start_Time
print("Recording Time is {}S".format(recording_time))
optris.terminate()

# plt.figure()
# plt.plot(times_computer-times_computer[0])
# plt.plot(np.linspace(0,1,1000))
# plt.show()
print("Mean Time per frame is {} s".format(recording_time/frames_captured))
print("Mean Freq per frame is {} Hz".format(frames_captured/recording_time))


