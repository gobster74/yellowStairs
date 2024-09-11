import pyOptris as optris
import time as time
import cv2
import numpy as np
import matplotlib.pyplot as plt

import concurrent.futures

# USB connection initialisation
optris.usb_init('generic.xml')

w, h = optris.get_thermal_image_size()

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

def your_function(w,h):
    # Get the palette image (RGB image)
    # Get the thermal frame (numpy array)
    thermal_frame = optris.get_thermal_image(w, h)
    # Conversion to temperature values are to be performed as follows:
    # t = ((double)data[x] - 1000.0) / 10.0;
    return (thermal_frame - 1000.0) / 10/1800*255,time.time()
start_time = time.time()
def schedule_function_with_interval(interval_ms, function,w,h):
    interval_sec = interval_ms / 1000.0
    results = []
    times =[]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for frame_n in range(1000):
            start_time = time.time()

            # Submit the function to the executor
            future = executor.submit(function,w,h)

            # Wait for the specified interval before scheduling the next function call
            elapsed_time = time.time() - start_time
            remaining_time = max(0, interval_sec - elapsed_time)
            time.sleep(remaining_time)

            # Ensure the function has completed before moving on to the next iteration
            result,timed = future.result()
            results.append(result)
            times.append(timed)
    return results,times
timed_finction = time.time()-start_time

print("Function took {}s to execute".format(timed_finction))

# Example usage
interval_ms = 1  # Call the function every millisecond

# Start scheduling the function with the specified interval
array,times_computer = schedule_function_with_interval(interval_ms, your_function,w,h)


plt.figure()
plt.plot(times_computer)

optris.terminate()
times_computer=np.array(times_computer)
DeltaT  = times_computer[1:-1]-times_computer[0:-2]
Freq = 1/DeltaT

print("Mean Time per frame is {} s".format(np.mean(DeltaT)))
print("Mean Freq per frame is {} Hz".format(np.mean(Freq)))

plt.plot(DeltaT)
plt.show()




cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL) 
# Using resizeWindow() 
cv2.resizeWindow("Resized_Window", w *5, h*5) 
for frame_n in range(1000):
    im_color = cv2.applyColorMap(convert_to_temperature_image(array[frame_n]),8)

    cv2.imshow("Resized_Window", im_color)
    times_computer[frame_n] = time.time()
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    time.sleep(0.01)