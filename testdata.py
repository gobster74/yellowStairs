import numpy as np
import cv2
import os
import glob

def list_saved_files():
    buffer_files = glob.glob('frame_buffer_*.npy')
    time_files = glob.glob('times_computer_*.npy')
    
    buffer_files.sort()  # Sort by filename
    time_files.sort()

    print("Available saved files:")
    for i, file in enumerate(buffer_files):
        print(f"{i}: {file}")

    return buffer_files, time_files

def load_saved_data(buffer_file, time_file):
    try:
        frame_buffer = np.load(buffer_file)
        times_computer = np.load(time_file)
        print(f"Loaded frame_buffer shape: {frame_buffer.shape}")
        print(f"Loaded times_computer shape: {times_computer.shape}")
    except FileNotFoundError:
        print(f"File not found: {buffer_file} or {time_file}")
        return None, None

    return frame_buffer, times_computer

def display_saved_data(frame_buffer, scale_factor=3):
    if frame_buffer is None:
        print("No frame buffer to display.")
        return

    h, w = frame_buffer.shape[1], frame_buffer.shape[2]

    # Create a window to display the frames
    cv2.namedWindow('Thermal Stream', cv2.WINDOW_NORMAL)
    for i, frame in enumerate(frame_buffer):
        # Normalize frame to 0-255 for display
        normalized_image = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
        display_image = np.uint8(normalized_image)

        # Apply a colormap to simulate the heatmap look of Optris PIX
        color_image = cv2.applyColorMap(display_image, cv2.COLORMAP_JET)

        # Resize the image for larger display
        resized_image = cv2.resize(color_image, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_LINEAR)

        # Show the frame in the same window
        cv2.imshow('Thermal Stream', resized_image)

        # Press 'q' to quit the display loop
        if cv2.waitKey(100) & 0xFF == ord('q'):
            print("Exiting display...")
            break

    # Close the window after the loop
    cv2.destroyWindow('Thermal Stream')

# Example to list, select, load, and display saved data
buffer_files, time_files = list_saved_files()

if buffer_files and time_files:
    selected_index = int(input(f"Enter the file index (0 to {len(buffer_files)-1}): "))
    
    if 0 <= selected_index < len(buffer_files):
        frame_buffer, times_computer = load_saved_data(buffer_files[selected_index], time_files[selected_index])
        
        if frame_buffer is not None and times_computer is not None:
            display_saved_data(frame_buffer)
    else:
        print("Invalid file index.")
else:
    print("No saved files found.")
