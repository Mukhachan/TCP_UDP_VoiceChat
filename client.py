import socket
import random
from threading import Thread
from datetime import datetime
from colorama import Fore, init, Back

from config import SERVER_HOST, SERVER_PORT, separator_token, CHUNK
from os import system

system("clear")
init()


colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, 
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, 
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]

client_color = random.choice(colors)



s = socket.socket()
host_ip = input("input server ip: ")
print(f"[*] Connecting to {host_ip}:{SERVER_PORT}...")
s.connect((host_ip, SERVER_PORT))
print("[+] Connected.")

name = input("Enter your name: ")

def listen_for_messages():
    while True:
        message = s.recv(CHUNK).decode()
        print("\n"+message) if message else None

t = Thread(target=listen_for_messages)
t.daemon = True
t.start()

while True:
    to_send = input("send message: ")
    if to_send.lower() == 'q':
        break
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    to_send = f"{client_color}[{date_now}] {name}{separator_token}{to_send}{Fore.RESET}"
    s.send(to_send.encode())

s.close()