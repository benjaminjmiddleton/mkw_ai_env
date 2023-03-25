import json
import socket
import time

DRIFT_LEFT = -2
WHEELIE_LEFT = -1
WHEELIE_FORWARD = 0
WHEELIE_RIGHT = 1
DRIFT_RIGHT = 2
DRIFT_FORWARD = 3

host = socket.gethostname()
port = 5555
sock = socket.socket()
sock.bind((host, port))
print("Waiting for connection from dolphin client...")
sock.listen(1)
client_socket, address = sock.accept()
print("Connection from: " + str(address))

with client_socket:
    while True:
        message = json.loads(client_socket.recv(131072).decode('utf-8'))
        if not message:
            break
        pixels = message[0]
        reward = message[1]
        frame_counter = message[2]

        if frame_counter % 60 == 0:
            print("pixels size:", len(pixels), len(pixels[0]), "reward:", reward, "frame:", frame_counter)

        if frame_counter >= 160 and frame_counter < 210:
            client_socket.send(json.dumps( (DRIFT_RIGHT, False) ).encode("utf-8"))
        elif frame_counter < 250:
            client_socket.send(json.dumps( (WHEELIE_FORWARD, False) ).encode("utf-8"))
        elif frame_counter == 1:
            # reset
            client_socket.send(json.dumps( (WHEELIE_FORWARD, True) ).encode("utf-8"))
        else:
            # Do nothing
            client_socket.send(json.dumps( (-3, False) ).encode("utf-8"))
client_socket.close()