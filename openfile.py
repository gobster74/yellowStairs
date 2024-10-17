import numpy as np
import cv2
from tkinter import filedialog
from PIL import Image, ImageTk
import tkinter as tk

def open_file():
    file_path = filedialog.askopenfilename(defaultextension=".bin",
                                           filetypes=[("Binary files", "*.bin")])
    if file_path:
        with open(file_path, 'rb') as f:
            data = np.load(f, allow_pickle=True).item()
            frame_buffer = data['frame_buffer']
            times_computer = data['times_computer']
            
            status_label.config(text=f"Loaded {len(frame_buffer)} frames.")
            display_frames(frame_buffer, times_computer)

def display_frames(frame_buffer, times_computer):
    def show_frame(idx):
        frame = frame_buffer[idx]
        timestamp = times_computer[idx]
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        label_img.imgtk = imgtk
        label_img.configure(image=imgtk)
        status_label.config(text=f"Displaying frame {idx + 1}/{len(frame_buffer)}, Time: {timestamp:.2f}s")

        if idx < len(frame_buffer) - 1:
            window.after(100, lambda: show_frame(idx + 1))

    show_frame(0)

def create_gui():
    global label_img, status_label, window

    window = tk.Tk()
    window.title("Thermal Camera Playback")
    window.geometry("800x600")

    frame_display = tk.Frame(window)
    frame_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    label_img = tk.Label(frame_display)
    label_img.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    open_button = tk.Button(window, text="Open Recording", command=open_file)
    open_button.pack(side=tk.LEFT, padx=5, pady=5)


    status_label = tk.Label(window, text="No file loaded")
    status_label.pack(side=tk.BOTTOM, padx=5, pady=5)


    quit_button = tk.Button(window, text="Quit", command=window.quit)
    quit_button.pack(side=tk.LEFT, padx=5, pady=5)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
