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

client_sockets = []

def listen_for_client(cs: socket.socket, client_address: tuple):
    while True:
        try:
            msg = cs.recv(CHUNK).decode()
        except Exception as e:
            print(f"[!] Error: {e}")
            dic = {
            "connection" : cs, 
            "address" : client_address
            }
            if dic in client_sockets: 
                client_sockets.remove(dic)
        else:
            # if we received a message, replace the <SEP> 
            # token with ": " for nice printing
            if msg != "":
                msg = msg.replace(separator_token, ": ")
                print(msg)
        i = 0
        ln_clients = len(client_sockets)
        while i < ln_clients:
            try:
                client_sockets[i]["connection"].send(msg.encode())
                i+=1
            except Exception as e:
                print("index", i)
                client_sockets.remove(client_sockets[i])
                print(f"[!] Error: {e}")


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

    if client_socket not in client_sockets:
        print("adding")
        client_sockets.append({
            "connection" : client_socket, 
            "address" : client_address})
    else:
        continue
    t = Thread(target=listen_for_client, args=(client_socket, client_address))

    t.daemon = True
    t.start()

    # for cs in client_sockets:
    #     cs: socket.socket
    #     cs.close()
