import socket
import pickle
import struct
import time
import zlib
from threading import Thread
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from ftplib import FTP

class MyHandler(FTPHandler):
    def on_file_received(self, fileHandler):
      with open(fileHandler, 'rb') as fh:
        data = pickle.load(fh)
      os.remove(fileHandler)
      for i in NetworkNode.nodes: 
        i.onReceived(data)
    def on_incomplete_file_received(self, file):
      os.remove(file)

class NetworkNode:
  nodes = []

  def __init__(self, curr, dest):
    self.host = curr[0] 
    self.port = int(curr[1])
    NetworkNode.nodes.append(self)
    self.dest = list( (i[0], int(i[1])) for i in dest )
    self.serv = Thread(target=self.start_server)
    self.serv.start()
    self.recieved = []

  def start_server(self):
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(os.getcwd(), perm='elradfmwMT')
    handler = MyHandler
    handler.authorizer = authorizer
    server = FTPServer((self.host, self.port), handler)
    server.max_cons = 2
    server.max_cons_per_ip = 5
    server.serve_forever()

  def onReceived(self, data):
    self.recieved.append(data)

  def generateName(self, cur = True):
    return ("send_" if cur else "grad_") + self.host + "_" + str(self.port) + ".bin"

  def sendData(self, dataObject):
    f = self.generateName()
    with open(f, "wb") as dataFile:
      pickle.dump(dataObject, dataFile)
    for c in self.dest:
      while True:
        try:
          with FTP() as ftp:
            print("FTP Connecting...")
            ftp.connect(c[0], c[1])
            print("Try login..")
            ftp.login()
            print("Set CWD")
            ftp.cwd('/')
            print("Sending file...")
            with open(f, "rb") as file:
              print("Binary:")
              ftp.storbinary(f"STOR {self.generateName(False)}", file)
            print("OK!")
          break
        except:
          print("Ошибка при попытке передаче данных. Повтор через 3 сек.")
          time.sleep(3)
    os.remove('./' + f)

  def waitGrads(self, count):
    return True if len(self.recieved) != count else False

  def clearRecv(self):
    self.recieved = []

if __name__ == "__main__":
  a = NetworkNode( ('127.0.0.1', 12401), [ ['127.0.0.1', 12000] ])
  time.sleep(2)
  data = {'test': 1}
  a.sendData( data )