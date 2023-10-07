import cv2
import socket
import struct
import pickle
import threading
import tkinter as tk
from tkinter import Label, Button, Canvas
from PIL import Image, ImageTk

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("127.0.0.1", 65001))#use any port but try for same post as serverside

root = tk.Tk()
root.title("Remote Control GUI")

canvas = Canvas(root, width=660, height=260)
canvas.pack()

telemetry_label = Label(root, text="Telemetry Data: Speed: 0 Battery: 100")
telemetry_label.pack()

def exit_program():
    client_socket.close()
    root.destroy()

exit_button = Button(root, text="Exit", command=exit_program)
exit_button.pack()

def update_video():
    while True:
        data, server_address = client_socket.recvfrom(65535)
        if data:
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

def receive_telemetry_data():
    while True:
        data, server_address = client_socket.recvfrom(1024)
        if data:
            telemetry_data = pickle.loads(data)
            telemetry_label.config(text=f"Telemetry Data: Speed: {telemetry_data['Speed']} Battery: {telemetry_data['Battery']}")

telemetry_thread = threading.Thread(target=receive_telemetry_data)
telemetry_thread.start()

root.mainloop()
