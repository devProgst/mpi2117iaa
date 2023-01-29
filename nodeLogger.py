
def cleanLog(saveFile):
  with open(saveFile + ".log", "w"): pass

def writeLog(saveFile, block, loss, acc):
  with open(saveFile + ".log", "a") as sf:
    data = map(str, [ block, loss, acc ])
    sf.write(",".join(data) + "\n")