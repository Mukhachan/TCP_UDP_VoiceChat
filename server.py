from datetime import datetime
import io
from pprint import pprint
import pyaudio
import socket
import numpy as np
import soundfile as sf
from threading import Thread
from time import sleep

from config import CHANNELS, CHUNK, FORMAT, RATE, SERVER_PORT, SERVER_HOST, separator_token
from converter import RAW_2_OGG, OGG_2_RAW
from os import system

system("clear")

client_sockets = set()

def listen_for_client(cs: socket.socket):
    while True:
        try:
            msg = cs.recv(CHUNK).decode()
        except Exception as e:
            print(f"[!] Error: {e}")
            if client_sockets: 
                client_sockets.remove(cs)
        else:
            # if we received a message, replace the <SEP> 
            # token with ": " for nice printing
            msg = msg.replace(separator_token, ": ")
            print(msg)
        for client_socket in client_sockets:
            client_socket: socket.socket
            
            client_socket.send(msg.encode())

sock = socket.socket(socket.AF_INET,
                    socket.SOCK_STREAM)
# Сделаем сокет используемым
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((SERVER_HOST, SERVER_PORT))

sock.listen(10)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")


while True:
    client_socket, client_address = sock.accept()
    print(f"[+] {client_address} connected.")

    client_sockets.add(client_socket)

    t = Thread(target=listen_for_client, args=(client_socket,))

    t.daemon = True
    t.start()

    # for cs in client_sockets:
    #     cs: socket.socket
    #     cs.close()
