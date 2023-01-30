import matplotlib.pyplot as plt
import glob

graphs = []
files = glob.glob('*_log.log')
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
plt.xlabel('Итерация (N)', color='gray')
plt.ylabel('Значение (%)',color='gray')

for gid, g in enumerate(graphs):
	plt.plot(range(len(g)), g, clrs[gid % len(clrs)] + '-')

plt.show()