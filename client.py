from datetime import datetime
import json
import base64, pickle
import socket
import pyaudio
from pydub import AudioSegment
from config import *
import numpy as np
import soundfile as sf
import threading
from os import system
import sys



class GetAudio:
    def __init__(self, sock: socket.socket, name: str) -> None:
        self.sock = sock
        self.pout = pyaudio.PyAudio()
        self.p_read = self.pout.open(output=True,
                            format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            frames_per_buffer=AUDIO_BLOCK)
        
        self.data_vhod, self.samplerate_vhod = sf.read('sounds/vhod.ogg')
        self.data_vihod, self.samplerate_vihod = sf.read('sounds/vihod.ogg')

        self.name = name
        self.buffer = ''


    def get_audio(self):
        """
            Генератор, который возвращает данные из потока аудио.
        """
        while True:
            message = sock.recv(CHUNK) # Получение сообщениe
            if message != "": 
                if SEP not in message:
                    self.buffer += message
                    continue
                else:
                    self.buffer = message.split(SEP)[1]
                message = json.loads((
                        self.buffer+message.split(SEP)[0]
                    ).decode("utf-8")) 
                               

                message['samplerate'] = AUDIO_BLOCK
                if message['event'] == 'connect':
                    print(f"{datetime.now()} - {message['nickname']} connected!")
                    # message['data'] = self.data_vhod
                    # message['samplerate'] = self.samplerate_vhod
                    ...

                elif message['event'] == 'disconnect':
                    print(f"{datetime.now()} - {message['nickname']} disconnected!")
                    # message['data'] = self.data_vihod
                    # message['samplerate'] = self.samplerate_vihod
                    ...

                elif message['event'] == 'Message':
                    message['data'] = base64.b64decode(message['data'])
                    print(message)
                    yield message

 
    def main(self):
        for data in self.get_audio():
            if data['data'] != "" and SOUND_CALLBACK and data['nickname'] == self.name:
                self.p_read.write(frames=data['data'], num_frames=data['samplerate'])

class SendMessages:
    def __init__(self, sock: socket.socket, name: str) -> None:
        self.sock = sock
        self.name = name

    def sendConnect(self) -> dict[bool, str]:
        """
            Отправляем пустое, сервисное сообщение о подключении нового пользователя
        """
        try:
            msg = {
                "nickname" : self.name,
                "data" : 1449+len(self.name.encode("utf-8")),
                "event" : "connect",
            }
            msg = json.dumps(msg).encode("utf-8")+SEP
            self.sock.send(msg)
            return {
                'Status' : True,
                'Message' : "Connect message sent"
            }
        except Exception as e:
            print(f"Error in `sendConnect`: {e}")
            return {
                'Status' : False,
                'Message' : f"Error in `sendConnect`: {e}"
            }

    def sendDisconnect(self) -> dict[bool, str]:
        """
            Отправляем пустое, сервисное сообщение об отключении пользователя
        """
        try:
            msg = {
                "nickname" : self.name,
                "data" : "",
                "event" : "disconnect",
            }
            msg = json.dumps(msg).encode("utf-8")+SEP
            self.sock.send(msg)
            return {
                'Status' : True,
                'Message' : "Disconnect message sent"
            }
        except Exception as e:
            print(f"Error in `sendDisconnect`: {e}")
            return {
                'Status' : False,
                'Message' : f"Error in `sendDisconnect`: {e}"
            }

    def sendMessage(self, data_block: bytes) -> dict[bool, str]:
        """
            Отправляем блок аудиоданных
        """
        try:
            # data_block = AudioSegment(
            #                 data=data_block, 
            #                 sample_width=SAMPLE_WIDTH,
            #                 frame_rate=RATE,
            #                 channels=CHANNELS
            # )

            msg = {
            "nickname" : self.name,
            "data" : base64.b64encode(data_block).decode("utf-8"),
            "event" : "Message",
            }
            msg = json.dumps(msg).encode("utf-8")+SEP
            self.sock.send(msg)

            return {
                'Status' : True,
                'Message' : "Message sent"
            }
        except Exception as e:
            print(f"Error in `sendMessage`: {e}")
            return {
                'Status' : False,
                'Message' : f"Error in `sendMessage`: {e}"
            }

class RecordAudio:
    def __init__(self, audio_file: str, sock: socket.socket, name: str):
        self.sock = sock
        self.audio_file = audio_file

        self.name = name

        self.pin = pyaudio.PyAudio()
        self.pout = pyaudio.PyAudio()
        # Стрим на запись
        self.p_stream = self.pin.open(input=True,
                            format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            frames_per_buffer=AUDIO_BLOCK, 
                            input_device_index=self.pin.get_default_input_device_info()['index']
                            )
        # Стрим на воспроизведение
        self.p_read = self.pout.open(output=True,
                            format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            frames_per_buffer=AUDIO_BLOCK)
        # Создаем пустой AudioSegment
        self.audio_segment = AudioSegment(
            data=b'', 
            sample_width=SAMPLE_WIDTH,
            frame_rate=RATE,
            channels=CHANNELS
        )
        # Отправляем сообщение о подключении пользователя
        self.SendMessages = SendMessages(self.sock, self.name)
        self.SendMessages.sendConnect()

    def record_audio(self):
        try:
            while True:
                # Читаем данные из потока
                audio_data = self.p_stream.read(AUDIO_BLOCK, exception_on_overflow = False)
                yield audio_data  # Возвращаем блок данных
        except KeyboardInterrupt:
            print("Запись прервана.")
        finally:
            # Закрываем поток и освобождаем ресурсы
            self.p_stream.stop_stream()
            self.p_stream.close()
            self.pin.terminate() 
            # self.pout.terminate()

    def main(self):
        print("Вы подключились к серверу. Нажмите Ctrl+C для остановки.")
        try:
            for audio_block in self.record_audio():
                # Отправляем аудио блок
                if not self.SendMessages.sendMessage(audio_block)["Status"]:
                    return False
        except KeyboardInterrupt:
            print("Disconnecting.")
            self.SendMessages.sendDisconnect()
            return True


# Пример использования функции
if __name__ == "__main__":
    # if sys.platform == "win32":
    #     system("cls")
    # else:
    #     system("clear")


    sock = socket.socket()
    print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
    sock.connect((SERVER_HOST, SERVER_PORT))
    print("[+] Connected.")
    name = input("send your name: ")

    GetAudio_ex = GetAudio(sock, name)
    RecordAudio_ex = RecordAudio("sounds/rec_new.ogg", sock, name)

    try:
        listen_thd = threading.Thread(target=GetAudio_ex.main)
        record_thd = threading.Thread(target=RecordAudio_ex.main)
        
        listen_thd.daemon = True
        listen_thd.start()
        record_thd.start()

        record_thd.join()
        listen_thd.join()

    except (KeyboardInterrupt, SystemExit):
        SendMessages(sock, name).sendDisconnect()
        sock.close()
        print("Stopping...")
