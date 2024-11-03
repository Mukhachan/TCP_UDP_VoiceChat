import pyaudio


CHUNK=1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 9100

separator_token = "<SEP>" # we will use this to separate the client name & message
