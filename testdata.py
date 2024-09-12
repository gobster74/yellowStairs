import numpy as np

def load_data(counter):
    # Define filenames based on the counter value
    frame_buffer_file = f'frame_buffer_{counter}.npy'
    times_computer_file = f'times_computer_{counter}.npy'
    
    try:
        # Load the data from files
        frame_buffer = np.load(frame_buffer_file)
        times_computer = np.load(times_computer_file)
        
        # Print shapes to confirm successful loading
        print(f"Loaded frame_buffer shape: {frame_buffer.shape}")
        print(f"Loaded times_computer shape: {times_computer.shape}")
        
        return frame_buffer, times_computer
    
    except FileNotFoundError as e:
        print(f"Error: {e}. Check if the file exists and the counter is correct.")
        return None, None

# Specify the counter value to load
counter_to_load = 8  # Change this to the desired counter value
frame_buffer, times_computer = load_data(counter_to_load)

if frame_buffer is not None and times_computer is not None:
    # Example usage of the loaded data
    # Display the first frame, for instance
    import matplotlib.pyplot as plt
    
    plt.imshow(frame_buffer[900], cmap='hot')
    plt.colorbar()
    plt.title(f'Frame {frame_buffer} from counter {counter_to_load}')
    plt.show()
