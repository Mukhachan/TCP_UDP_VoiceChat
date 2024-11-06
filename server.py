import base64
from datetime import datetime
import io
import json
import pickle
from pprint import pprint
from colorama import Fore
import pyaudio
import socket
import numpy as np
import soundfile as sf
from threading import Thread
from time import sleep

from config import CHANNELS, CHUNK, FORMAT, RATE, SERVER_PORT, SERVER_HOST

from os import system
system("clear")

client_sockets = []

def messageSending(msg: str, from_address: tuple):
    if msg["event"] == "connect":
        mess_to_send = {
            "nickname" : "[System]",
            "data" : (f"{Fore.LIGHTBLACK_EX}[System]: {msg['nickname']} connected!{Fore.RESET}\n"),
            "event": "connect",
        }
    elif msg["event"] == "disconnect":
        mess_to_send = {
            "nickname" : "[System]",
            "data" : (f"{Fore.LIGHTBLACK_EX}[System]: {msg['nickname']} disconnected!{Fore.RESET}\n"),
            "event": "disconnect",
        }
        for i in range(client_sockets):
            if client_sockets[i]["address"] == from_address:
                client_sockets.remove(client_sockets[i])
    elif msg["event"] == "message":
        mess_to_send = msg
    else: return

    ln_clients = len(client_sockets)
    i = 0    
    while i < ln_clients:
        try:
            mess_to_send = base64.b64encode(pickle.dumps(mess_to_send))
            print("try to send msg")
            client_sockets[i]["connection"].send(mess_to_send)

        except Exception as e:
            print("index", i)
            print(f"[!] Error in messageSending: {e}")
            if "Broken pipe" in str(e):
                client_sockets.remove(client_sockets[i])
                ln_clients-=1
        i+=1

def listen_for_client(cs: socket.socket, client_address: tuple):
    while True:
        try:
            msg = cs.recv(CHUNK)
            if msg: 
                msg = pickle.loads(base64.b64decode(msg.decode()))
                print(msg) if msg['event'] != 'message' else None
                
            else: continue

        except Exception as e:
            print(f"Error in listen_for_client: {e}")
            return
        
        if not msg: continue
        if msg["event"] == "connect":
            client = {
                    "nickname": msg["nickname"],
                    "connection" : cs, 
                    "address" : client_address
                    }
            if client not in client_sockets:
                client_sockets.append(client)
            else:
                continue
        
        messageSending(msg, client_address)

def eval_check():
    while True:
        try:
            eval(input())
        except Exception as e:
            print(f"eval() Error: {e}")


def main():
    sock = socket.socket(socket.AF_INET,
                        socket.SOCK_STREAM)
    # Сделаем сокет используемым
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER_HOST, SERVER_PORT))

    sock.listen(10)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    ev_check_thrd = Thread(target=eval_check, args=())
    ev_check_thrd.start()

    while True:
        client_socket, client_address = sock.accept()
        print(f"[+] {client_address} connected.")


        listen_for_client_thrd = Thread(target=listen_for_client, args=(client_socket, client_address))
        listen_for_client_thrd.daemon = True
        listen_for_client_thrd.start()

        # for cs in client_sockets:
        #     cs: socket.socket
        #     cs.close()

if __name__ == "__main__":
    main()