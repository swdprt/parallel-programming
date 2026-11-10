import matplotlib.pyplot as plt
from collections import defaultdict

data = defaultdict(lambda: defaultdict(list))  # data[N][P] = [ms, ms, ms]

with open("timings.txt") as f:
    next(f)
    for line in f:
        n, p, t = line.strip().split(",")
        data[int(n)][int(p)].append(float(t))

plt.figure(figsize=(10, 6))
for p in sorted({p for n in data for p in data[n]}):
    xs = sorted(n for n in data if p in data[n])
    ys = [sum(data[n][p]) / len(data[n][p]) for n in xs]
    plt.plot(xs, ys, marker='o', label=f'{p} проц.')

plt.title('Время умножения матриц (MPI) от размера')
plt.xlabel('Размер матрицы N')
plt.ylabel('Время, мс')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.savefig('graph.png', dpi=150)
print("graph.png сохранён")