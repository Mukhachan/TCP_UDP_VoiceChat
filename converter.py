import io
import numpy as np
import soundfile as sf

from config import RATE

def RAW_2_OGG(raw_chunk):
  byte_io = io.BytesIO()
  signal = np.frombuffer(raw_chunk,dtype=np.float32)
  
  sf.write(byte_io, signal, RATE,format='OGG') 
  
  return bytes(byte_io.getbuffer())


def OGG_2_RAW(ogg_chunk) -> np.float32:
  byte_io = io.BytesIO()
  byte_io.write(ogg_chunk)
  byte_io.seek(0)
  
  data, samplerate = sf.read(byte_io)
  
  return np.float32(data)