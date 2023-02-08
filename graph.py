import matplotlib.pyplot as plt
from glob import glob
trains = []
files = glob("*.log")
clrs = [ 'b', 'g', 'r', 'c', 'm', 'k', 'y' ]
for f in files:
    with open(f, "r") as file:
        pick = []
        for l in file.read().splitlines():
            data = l.split(",")
            if data[0] == 'main':
                pick.append( [float(data[1]), float(data[2])] )
        trains.append(pick)

plt.title('График обучения', fontsize=20, fontname='Times New Roman')
plt.xlabel('Шаг (N)', color='gray')
plt.ylabel('Значение (%)',color='gray')

maxX, minY, maxY = [ None ] * 3
for tid, t in enumerate(trains):
    plt.plot(range(0,len(t)), list(a[1] for a in t), clrs[tid] + '-', label=("точность #" + str(tid)) if len(trains) > 0 else "точность local")
    plt.plot(range(0,len(t)), list(a[0] for a in t), clrs[tid] + '-', label=("ошибка #" + str(tid)) if len(trains) > 0 else "ошибка local")
 
plt.grid(linewidth=1, color='0.95', axis='x')

plt.legend()
plt.show()