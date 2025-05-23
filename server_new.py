import base64
from datetime import datetime
import json
import pickle
import socket

import json.scanner
from config import *
from threading import Thread

# from os import system
# system('clear')

class Server:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((SERVER_HOST_BIND, SERVER_PORT))
        print("Server started")
        self.sock.listen(MAX_CONNECTIONS)
        self.users = []


    def sendMsgs(self, from_user_addr: tuple, data: bytes):
        """ Отправляем сообщения всем подключенным клиентам """
        for user in self.users:
            if  user != from_user_addr:
                self.sock.sendto(data, user)

    def checkMsgs(self, from_user_sock: socket.socket, from_user_addr: tuple, buffer: str = ''):
        while True:
            try:
                msg = from_user_sock.recv(CHUNK)
                msg = msg.replace("'", "\"").strip()
                if msg:
                    if SEP not in msg:
                        buffer += msg
                        continue
                    else:
                        buffer = msg.split(SEP)[1]

                    msg_dec = json.loads((
                            buffer+msg.split(SEP)[0]
                        ).decode("utf-8"))
                    
                    if msg_dec['event'] == "disconnect":
                        from_user_sock.close()
                        self.users.remove(from_user_addr)
                        print(msg_dec)
                        break
                    elif msg_dec['event'] == "connect":
                        print(msg_dec)
                    elif msg_dec['event'] == "Message":
                        pass
                        
                    else:
                        print("Неизвестный запрос")
                    
                    # Отправляем звук всем пользователям
                    self.sendMsgs(from_user_addr, msg)
                    
                    # отправляем звук пользователю обратно
                    from_user_sock.send(msg)
                else: continue

            except Exception as e:
                print(f"Error in checkMsgs: {e.__class__} {e}")
                print(buffer, msg)
                if "Connection reset" in str(e) or "roken pipe" in str(e):
                    self.users.remove(from_user_addr)
                    break

    def main(self):
        while len(self.users)<=MAX_CONNECTIONS:
            client_socket, client_address = self.sock.accept()
            self.users.append(client_address)

            users_thd = Thread(target=self.checkMsgs, args=(client_socket, client_address))
            users_thd.start()
            print(f"({datetime.now()}) - New connection from {client_address}")
        return True


if __name__=="__main__":
    Server_ex = Server()
    Server_ex.main()