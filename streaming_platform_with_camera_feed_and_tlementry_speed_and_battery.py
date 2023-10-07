import cv2
import socket
import struct
import pickle
import threading
import tkinter as tk
from tkinter import Label, Button, Canvas
from PIL import Image, ImageTk

# Constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
MAX_PACKET_SIZE = 65507

# Video streaming setup for two cameras
cap1 = cv2.VideoCapture(0)  # Camera 1 (adjust index as needed)
cap1.set(3, 320)  # Set the width of the video frame
cap1.set(4, 240)  # Set the height of the video frame

cap2 = cv2.VideoCapture(1)  # Camera 2 (adjust index as needed)
cap2.set(3, 320)  # Set the width of the video frame
cap2.set(4, 240)  # Set the height of the video frame

# Socket setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Telemetry data (simulated)
telemetry_data = {"Speed": 0, "Battery": 100}

# Functions to send video frames and telemetry data
def send_video(cam, camera_name):
    while True:
        ret, frame = cam.read()
        data = pickle.dumps(frame)
        packet_size = len(data)
        num_packets = packet_size // MAX_PACKET_SIZE + 1

        for i in range(num_packets):
            start = i * MAX_PACKET_SIZE
            end = (i + 1) * MAX_PACKET_SIZE
            packet = struct.pack("<L", len(data[start:end])) + data[start:end]

            client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))

def send_telemetry_data():
    while True:
        telemetry_msg = pickle.dumps(telemetry_data)
        client_socket.sendto(telemetry_msg, (SERVER_IP, SERVER_PORT))

        # Simulate telemetry data update
        telemetry_data["Speed"] += 1
        if telemetry_data["Speed"] > 100:
            telemetry_data["Speed"] = 0

        telemetry_data["Battery"] -= 1
        if telemetry_data["Battery"] < 0:
            telemetry_data["Battery"] = 100

        # Update telemetry label
        telemetry_label.config(text=f"Telemetry Data: Speed: {telemetry_data['Speed']} Battery: {telemetry_data['Battery']}")

# Start video and telemetry threads for both cameras
video_thread1 = threading.Thread(target=send_video, args=(cap1, "Camera 1"))
video_thread2 = threading.Thread(target=send_video, args=(cap2, "Camera 2"))
telemetry_thread = threading.Thread(target=send_telemetry_data)

video_thread1.start()
video_thread2.start()
telemetry_thread.start()

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
    cap1.release()
    cap2.release()
    client_socket.close()
    root.destroy()

exit_button = Button(root, text="Exit", command=exit_program)
exit_button.pack()

# Function to update video feed in the GUI
def update_video():
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if ret1 and ret2:
        _extracted_from_update_video_6(frame1, frame2)
    root.after(10, update_video)


# TODO Rename this here and in `update_video`
def _extracted_from_update_video_6(frame1, frame2):
    frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
    frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)

    # Convert frames to Tkinter PhotoImage objects
    photo1 = ImageTk.PhotoImage(image=Image.fromarray(frame1))
    photo2 = ImageTk.PhotoImage(image=Image.fromarray(frame2))

    # Update the canvas with the images
    canvas.create_image(0, 0, anchor=tk.NW, image=photo1)
    canvas.create_image(330, 0, anchor=tk.NW, image=photo2)

    # Keep references to avoid garbage collection
    canvas.photo1 = photo1
    canvas.photo2 = photo2

update_video()

root.mainloop()
