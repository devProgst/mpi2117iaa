import os
import pickle
import time
from threading import Thread
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
    authorizer.add_user(username='user', password='passwrd', homedir=os.getcwd(), perm='elradfmwMT')
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
            ftp.connect(c[0], c[1])
            ftp.login('user','passwrd')
            ftp.cwd('/')
            with open(f, "rb") as file:
              ftp.storbinary(f"STOR {self.generateName(False)}", file)
          break
        except:
          print("Ошибка при попытке передаче данных. Повтор через 3 сек.")
          time.sleep(3)
    os.remove('./' + f)

  def waitGrads(self, count):
    return True if len(self.recieved) != count else False

  def clearRecv(self):
    self.recieved = []