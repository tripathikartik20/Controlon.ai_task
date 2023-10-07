import cv2
import socket
import struct
import pickle
import threading
import tkinter as tk
from tkinter import Label, Button, Canvas
from PIL import Image, ImageTk

# Constants
SERVER_IP = "127.0.0.1"  # Replace with the IP address of the server machine
SERVER_PORT = 12345

# Socket setup for receiving video frames and telemetry data
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("127.0.0.1", 65001))  # Bind to any available port

# GUI
root = tk.Tk()
root.title("Remote Control GUI")

# Create a canvas for video display
canvas = Canvas(root, width=660, height=260)
canvas.pack()

# Create labels for telemetry data
telemetry_label = Label(root, text="Telemetry Data: Speed: 0 Battery: 100")
telemetry_label.pack()

# Exit button
def exit_program():
    client_socket.close()
    root.destroy()

exit_button = Button(root, text="Exit", command=exit_program)
exit_button.pack()

# Function to update video feed in the GUI
def update_video():
    while True:
        data, server_address = client_socket.recvfrom(65535)
        if data:
            # Extract video frames from received data
            frame_size = struct.unpack("<L", data[:4])[0]
            frame_data = data[4:4 + frame_size]
            frame = pickle.loads(frame_data)
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.photo = photo
        
        root.update()

video_thread = threading.Thread(target=update_video)
video_thread.start()

# Function to receive and display telemetry data
def receive_telemetry_data():
    while True:
        data, server_address = client_socket.recvfrom(1024)
        if data:
            telemetry_data = pickle.loads(data)
            telemetry_label.config(text=f"Telemetry Data: Speed: {telemetry_data['Speed']} Battery: {telemetry_data['Battery']}")

telemetry_thread = threading.Thread(target=receive_telemetry_data)
telemetry_thread.start()

root.mainloop()
