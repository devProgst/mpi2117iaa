import matplotlib.pyplot as plt
from glob import glob
graphs = []
files = glob("*.log")
clrs = [ 'b', 'g', 'r', 'c', 'm', 'k', 'y' ]
for f in files:
	with open(f, "r") as file:
		ga = []
		for l in file.read().splitlines():
			data = l.split(",")
			if data[0] == 'main':
				ga.append(float(data[2]))
		graphs.append(ga)

plt.title('График обучения', fontsize=20, fontname='Times New Roman')
plt.xlabel('Шаг (N)', color='gray')
plt.ylabel('Значение (%)',color='gray')

plt.grid(linewidth=1, color='0.95', axis='x')
maxX, minY, maxY = [ None ] * 3
for gid, g in enumerate(graphs):
	plt.plot(range(0,len(g)), g, clrs[gid] + '-')
	if (maxX == None or len(g) > maxX): maxX = len(g)
	if (minY == None or minY > min(g)): minY = min(g)
	if (maxY == None or maxY < max(g)): maxY = max(g)
plt.vlines(range(0,maxX,3), minY, maxY, colors=None, linewidth=1, color=['g'], linestyle=":")

plt.show()