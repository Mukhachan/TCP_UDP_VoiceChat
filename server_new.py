import base64
import json
import pickle
import socket
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
        self.buffer = ''

    def sendMsgs(self, from_user_addr: tuple, data: bytes):
        """ Отправляем сообщения всем подключенным клиентам """
        for user in self.users:
            if  user != from_user_addr:
                self.sock.sendto(data, user)

    def checkMsgs(self, from_user_sock: socket.socket, from_user_addr: tuple):
        while True:
            try:
                msg = from_user_sock.recv(CHUNK)
                if msg: 
                    if SEP not in msg:
                        self.buffer += msg
                        continue
                    else:
                        self.buffer = msg.split(SEP)[1]

                    msg_dec = json.loads((
                            self.buffer+msg.split(SEP)[0]
                        ).decode("utf-8"))
                    
                    if msg_dec['event'] == "disconnect":
                        from_user_sock.close()
                        self.users.remove(from_user_addr)
                        print(msg_dec)
                        break
                    elif msg_dec['event'] == "connect":
                        print(msg_dec)
                    elif msg_dec['event'] == "Message":
                        print("Длина пакета", len(msg))
                        
                    else:
                        print("Неизвестный запрос")
                    
                    # Отправляем звук всем пользователям
                    self.sendMsgs(from_user_addr, msg)
                    
                    # отправляем звук пользователю обратно
                    from_user_sock.send(msg)
                else: continue

            except Exception as e:
                print(f"Error in checkMsgs: {e}")
                if "Connection reset" in str(e) or "roken pipe" in str(e):
                    self.users.remove(from_user_addr)
                    break

    def main(self):
        while len(self.users)<=MAX_CONNECTIONS:
            client_socket, client_address = self.sock.accept()
            self.users.append(client_address)

            users_thd = Thread(target=self.checkMsgs, args=(client_socket, client_address))
            users_thd.start()
            print(f"New connection from {client_address}")
        return True


if __name__=="__main__":
    Server_ex = Server()
    Server_ex.main()