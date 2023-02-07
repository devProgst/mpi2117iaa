
def cleanLog(saveFile):
  with open(saveFile, "w"): pass

def writeLog(saveFile, block, loss, acc, comment = None):
  with open(saveFile, "a") as sf:
    data = map(str, [ block, loss, acc ])
    sf.write(",".join(data) + (("#" + comment) if comment else "") + "\n")