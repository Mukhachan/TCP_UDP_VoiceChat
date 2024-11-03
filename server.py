from datetime import datetime
import io
from pprint import pprint
from colorama import Fore
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

def messageSending(msg: str, isFirst: bool, isDisconnected: str=False):
    ln_clients = len(client_sockets)
    for i in range(ln_clients - 1):
        try:
            if isDisconnected:
                client_sockets[i]["connection"].send((isDisconnected + " disconnected").encode())
            else:
                client_sockets[i]["connection"].send((Fore.LIGHTBLACK_EX + "[System]: " + msg + " connected!" + "\n").encode() if isFirst else msg.encode())
        except Exception as e:
            print("index", i)
            client_sockets.remove(client_sockets[i])
            print(f"[!] Error: {e}")
            break

def listen_for_client(cs: socket.socket, client_address: tuple):
    isFirst = True
    while True:
        try:
            msg = cs.recv(CHUNK).decode()
        except Exception as e:
            print(f"[!] Error: {e}")
            for i in range(len(client_sockets) - 1):
                if client_sockets[i]["address"] == client_address:
                    messageSending(msg, isFirst, isDisconnected=client_sockets[i]["nickname"])
                    print(client_sockets)
                    client_sockets.remove(client_sockets[i])
            break
        else:
            # if we received a message, replace the <SEP> 
            # token with ": " for nice printing
            if msg != "":
                msg = msg.replace(separator_token, ": ")
                print(msg)

        if isFirst:
            for i in range(len(client_sockets)):
                if client_sockets[i]["address"] == client_address:
                    client_sockets[i]["nickname"] = msg
        messageSending(msg, isFirst)
        isFirst = False


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
            "address" : client_address,
            "nickname": None})
    else:
        continue
    t = Thread(target=listen_for_client, args=(client_socket, client_address))

    t.daemon = True
    t.start()

    # for cs in client_sockets:
    #     cs: socket.socket
    #     cs.close()
