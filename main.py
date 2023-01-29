import sock
import model
import time
import sys

if len(sys.argv) != 5: 
  print("args: part[0-5] ip:port ip:port_1 ip:port_2")
  exit()
netMe = sys.argv[2].split(':') if ":" in sys.argv[2] else ['localhost', sys.argv[2]]
netN1 = sys.argv[3].split(':') if ":" in sys.argv[3] else ['localhost', sys.argv[2]]
netN2 = sys.argv[4].split(':') if ":" in sys.argv[4] else ['localhost', sys.argv[2]]

net = sock.NetworkNode(netMe, [netN1, netN2])
mod = model.Model(6, netMe[0]+"_"+str(netMe[1]) + "_log")
print("loading...")
time.sleep(5)

while True:
  mod.setRandomDS() # взять часть датасета
  localGrads = mod.train() # обучить и получить градиенты
  net.sendData( localGrads ) # отправить градиенты клиентам
  while len(net.recieved) != 2: # ожидание ответных градиентов
    print("Wait gradients...", end="\r")
    time.sleep(1)
  print("Gradients is okay!")
  mod.aggAndApplyGrads([localGrads] + net.recieved) # применение градиентов
  net.clearRecv() # очистка приемки
