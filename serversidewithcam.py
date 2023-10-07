import cv2
import socket
import struct
import pickle
import threading

# Constants
SERVER_IP = "127.0.0.1"  # Listen on all available network interfaces
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
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Telemetry data (simulated)
telemetry_data = {"Speed": 0, "Battery": 100}

# Functions to send video frames and telemetry data to the client
def send_video(client_address, cam):
    while True:
        ret, frame = cam.read()
        data = pickle.dumps(frame)
        packet_size = len(data)
        num_packets = packet_size // MAX_PACKET_SIZE + 1

        for i in range(num_packets):
            start = i * MAX_PACKET_SIZE
            end = (i + 1) * MAX_PACKET_SIZE
            packet = struct.pack("<L", len(data[start:end])) + data[start:end]

            server_socket.sendto(packet, client_address)

def send_telemetry_data(client_address):
    while True:
        telemetry_msg = pickle.dumps(telemetry_data)
        server_socket.sendto(telemetry_msg, client_address)

# Start video and telemetry threads for both cameras
video_thread1 = threading.Thread(target=send_video, args=(("client_address", 12345), cap1))
video_thread2 = threading.Thread(target=send_video, args=(("client_address", 12345), cap2))
telemetry_thread = threading.Thread(target=send_telemetry_data, args=(("client_address", 12345),))

video_thread1.start()
video_thread2.start()
telemetry_thread.start()

while True:
    pass  # Keep the server running indefinitely
