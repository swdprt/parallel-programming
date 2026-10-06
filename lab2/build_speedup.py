import matplotlib.pyplot as plt

def load(fname):
    sizes, times = [], []
    with open(fname) as f:
        for line in f:
            line = line.strip()
            if line:
                n, t = line.split(",")
                sizes.append(int(n)); times.append(float(t))
    return sizes, times

sizes, t1 = load("timings_1.txt")
_,     t2 = load("timings_2.txt")
_,     t4 = load("timings_4.txt")
_,     t8 = load("timings_8.txt")

plt.figure(figsize=(10, 6))
plt.plot(sizes, [a/b for a,b in zip(t1,t2)], marker='s', label='2 потока')
plt.plot(sizes, [a/b for a,b in zip(t1,t4)], marker='^', label='4 потока')
plt.plot(sizes, [a/b for a,b in zip(t1,t8)], marker='D', label='8 потоков')
plt.axhline(y=1, color='k', linestyle='--', alpha=0.5)
plt.title('Ускорение относительно 1 потока')
plt.xlabel('Размер матрицы N')
plt.ylabel('Speedup = T1 / Tp')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.savefig('speedup.png', dpi=150)
plt.show()