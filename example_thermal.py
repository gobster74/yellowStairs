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

def convert_to_temperature_image(temperature_array):
    # Normalize the temperature values to the range [0, 255] for display
    normalized_temperature = ((temperature_array - np.min(temperature_array)) / 
                              (np.max(temperature_array) - np.min(temperature_array)) * 255).astype(np.uint8)

    # Ensure that the normalized values are within the range [0, 255]
    normalized_temperature = np.clip(normalized_temperature, 0, 255)

    # Create a colormap (you can customize this based on your preference)
    colormap = cv2.applyColorMap(normalized_temperature, cv2.COLORMAP_JET)

    return colormap


wp, hp = optris.get_palette_image_size()

frames_captured = 5000

frame_buffer = np.empty((72,56,4*1000))
times_computer =  np.empty((1000))


start_Time = time.time()

times =[]
counter = 2000
frame_counter = 0
for count in range(frames_captured):
    if frame_counter%counter ==0:
        times.append(time.time()-start_Time)
        if len(times)>3:
            print("Mean Time per frame is {} s".format((times[-1]-times[-2])/counter))
            print("Mean Freq per frame is {} Hz".format(counter/(times[-1]-times[-2])))
    optris.get_thermal_image(w, h)


    frame_counter +=1
        






    
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


