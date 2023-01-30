# import socket
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from ftplib import FTP
import pickle
import struct
import time
import zlib
import hashlib as hl
from threading import Thread

class FTPMyHandler(FTPHandler):
  def on_connect(self):
    print("%s:%s connected" % (self.remote_ip, self.remote_port))
  def on_file_received(self, file):
    pass

class NetworkNode:
  def __init__(self, curr, dest):
    self.host = curr[0] 
    self.port = int(curr[1])
    self.dest = list( (i[0], int(i[1])) for i in dest )
    self.recieved = []
    
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous("./", perm="eldraw")
    handler = FTPMyHandler
    handler.authorizer = authorizer
    handler.on_connect = self.on_connect
    handler.on_file_received = self.on_gradients_received
    self.server = FTPServer((self.host, self.port), handler)
    ftpthread = Thread(target=self.startFTPServer)
    ftpthread.start()

  def startFTPServer(self):
    print("FTP Server started.")
    self.server.serve_forever()

  def on_connect(self):
    print("CONNECTED!")

  def on_gradients_received(self, file):
    print("Gradients received!")
    with open(file, 'rb') as f:
      self.recieved.append( pickle.loads( zlib.decompress( f.read() ) ) )
    os.remove(file)

  def chunked(self, size, source):
    for i in range(0, len(source), size):
      yield source[i:i+size]

  def sendData(self, obj):
    fileName = "g_" + self.host + "_" + str(self.port) + ".bin"
    # formFile:
    with open("./" + fileName, "wb") as f:
      f.write( zlib.compress( pickle.dumps( obj ) ) )
    print("Original grads archive created -", fileName)
    # sendFile to clients:
    for dest in self.dest:
      saveName = "grads_" + self.host + "_" + str(self.port) + "_" + str(dest[1]) + ".bin"
      print("Try to send grads as -", saveName)
      ftp = FTP('')
      ftp.connect(dest[0], dest[1])
      ftp.login()
      ftp.cwd('./')
      ftp.storbinary('STOR '+saveName, open(fileName, 'rb'))
      ftp.quit()
      print("Sended!")
    # delLocal
    os.remove("./" + fileName)

  def clearRecv(self):
    self.recieved = []