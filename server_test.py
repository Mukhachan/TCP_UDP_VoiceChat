import base64
import pickle
import socket
from config import *
from os import system
system("clear")

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("127.0.0.1", 9100))
print("Server started")
sock.listen(10)

client_socket, client_address = sock.accept()


from pydub import AudioSegment



while True:
        try:
            msg = client_socket.recv(CHUNK)
            if msg: 
                msg_dec = pickle.loads(base64.b64decode(msg.decode()))
                if msg_dec['event'] != "Message": 
                    if msg_dec['event'] == "disconnect":
                        client_socket.close()
                        break
                    print(msg_dec)

                client_socket.send(msg)
            else: continue

        except Exception as e:
            print(f"Error in listen_for_client: {e}")
            break
