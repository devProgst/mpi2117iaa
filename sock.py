import socket
import pickle
import struct
import time
import zlib
import hashlib as hl
from threading import Thread

class NetworkNode:
  def __init__(self, curr, dest):
    self.host = curr[0] 
    self.port = int(curr[1])
    self.dest = list( (i[0], int(i[1])) for i in dest )
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((self.host, self.port))
    self.sock.listen()
    
    self.recieved = []
    self.clients_threads = {}
    self.accept_thread = Thread(target=self.onConnection)
    self.accept_thread.start()

  def onConnection(self):
    while True:
      conn, addr = self.sock.accept()
      self.clients_threads[addr] = Thread(target=self.onReceiving, args=(conn, addr))
      self.clients_threads[addr].start()

  def onReceiving(self, conn, addr):
    try:
      size_in_4_bytes = conn.recv(4)
      size = struct.unpack('I', size_in_4_bytes)
      size = size[0]
      conn.send(b'1')
      dataRecv = b''
      while size > 0:
        data = conn.recv(32 + (1024 if (size > 1024) else size))
        if data[:32].decode('utf-8') == hl.md5(data[32:]).hexdigest():
          data = zlib.decompress(data[32:])
          dataRecv = pickle.loads(data)
          conn.send(b'1')
        else: 
          conn.send(b'0')
      self.recieved.append(dataRecv)
    except Exception as e:
      print("[ERROR] while recieving:", e)
      print("data start: ", data[:16])
    conn.close()
    del self.clients_threads[addr]

  def chunked(self, size, source):
    for i in range(0, len(source), size):
      yield source[i:i+size]

  def sendData(self, dataObject):
    tries = 3
    for dest in self.dest:
      while True:
        try:
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sendSocket:
            sendSocket.connect(dest)
            data = zlib.compress( pickle.dumps( dataObject ) )
            size = struct.pack("I", len(data))
            sendSocket.send(size)
            wait = sendSocket.recv(1)
            if wait == b'1':
              for i in self.chunked(1024, data):
                while True:
                  sendSocket.send(hl.md5(i).hexdigest().encode('utf-8') + i)
                  if sendSocket.recv(1) == b'1': break
                  if tries <= 0: return
                  tries -= 1
              print("Data sending is OK")
            else:
              print("Protocol error. Try to send again...")
        except Exception as e:
          print("[ERROR] while sending:", e)
          time.sleep(2)

  def clearRecv(self):
    self.recieved = []