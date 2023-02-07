import socket
import pickle
import struct
import time
import zlib
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
      data = zlib.decompress( conn.recv(size) )
      self.recieved.append( pickle.loads(data) )
    except Exception as e:
      print("ERROR while recieving!", e)
      print("data start: ", data[:16])
    conn.close()
    del self.clients_threads[addr]

  def sendData(self, dataObject):
    for dest in self.dest:
      while True:
        try:
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sendSocket:
            sendSocket.connect(dest)
            data = pickle.dumps(dataObject)
            size = len(data)
            size_in_4_bytes = struct.pack('I', size)
            sendSocket.send(size_in_4_bytes)
            wait = sendSocket.recv(1)
            if wait == b'1':
              sendSocket.send(zlib.compress(data))
              break
            else:
              print("Protocol error.. Retrying sending.")
        except:
          print("Error while sending.. Retrying...")
          time.sleep(2)

  def waitGrads(self, count):
    return True if len(self.recieved) != count else False

  def clearRecv(self):
    self.recieved = []