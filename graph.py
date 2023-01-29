import matplotlib.pyplot as plt

graphs = []
files = [ 'localhost_20000_log.log', 'localhost_20001_log.log', 'localhost_20002_log.log', 'localhost_20003_log.log', 'localhost_20004_log.log', 'localhost_20005_log.log' ]
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
	plt.plot(range(len(g)), g, clrs[gid] + '-')

plt.show()