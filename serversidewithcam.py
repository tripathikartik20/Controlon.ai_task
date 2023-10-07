import cv2
import socket
import struct
import pickle
import threading

from clientsidewithremote import SERVER_PORT

SERVER_IP = "127.0.0.1"
MAX_PACKET_SIZE = 65507

cap1 = cv2.VideoCapture(0)
cap1.set(3, 320)
cap1.set(4, 240)

cap2 = cv2.VideoCapture(1) 
cap2.set(3, 320)
cap2.set(4, 240)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

telemetry_data = {"Speed": 0, "Battery": 100}

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

video_thread1 = threading.Thread(target=send_video, args=(("client_address", 12345), cap1))
video_thread2 = threading.Thread(target=send_video, args=(("client_address", 12345), cap2))
telemetry_thread = threading.Thread(target=send_telemetry_data, args=(("client_address", 12345),))

video_thread1.start()
video_thread2.start()
telemetry_thread.start()

while True:
    pass  