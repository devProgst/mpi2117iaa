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
      for i in NetworkNode.nodes.keys(): 
        NetworkNode[i].onReceived(str(fileHandler))
    def on_incomplete_file_received(self, file):
      os.remove(file)

class NetworkNode:
  nodes = {}

  def __init__(self, curr, dest):
    self.host = curr[0] 
    self.port = int(curr[1])
    NetworkNode.nodes[ self.host + ":" + str(self.port) ] = self
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

  def onReceived(self, filepath):
    with open(filepath, 'rb') as f:
      self.recieved.append( zlib.decompress(pickle.load(f)) )
    os.remove(filepath)

  def generateName(self, cur = True):
    return ("send_" if cur else "grad_") + self.host + "_" + str(self.port) + ".bin"

  def sendData(self, dataObject):
    f = self.generateName()
    with open(f, "wb") as dataFile:
      dataFile.write( zlib.compress(pickle.dumps(dataObject)) )
    for c in self.dest:
      ftp = FTP()
      ftp.connect(c[0], c[1])
      ftp.login()
      ftp.cwd('/')
      with open(f, "rb") as file:
        ftp.storbinary(f"STOR {self.generateName(False)}", file)
      ftp.close()
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