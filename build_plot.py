import matplotlib.pyplot as plt

series = [
    ("timings_1.txt", 'b', 'o', '1 поток'),
    ("timings_2.txt", 'g', 's', '2 потока'),
    ("timings_4.txt", 'r', '^', '4 потока'),
    ("timings_8.txt", 'm', 'D', '8 потоков'),
]

plt.figure(figsize=(12, 7))

for fname, color, marker, label in series:
    sizes, times = [], []
    try:
        with open(fname) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                n, t = line.split(",")
                sizes.append(int(n))
                times.append(float(t))
        plt.plot(sizes, times, marker=marker, linestyle='-',
                 color=color, linewidth=2, label=label)
    except FileNotFoundError:
        print(f"Файл {fname} не найден, пропускаем")

plt.title('Зависимость времени перемножения матриц от размера\n(OpenMP, разное число потоков)')
plt.xlabel('Размер входной матрицы N')
plt.ylabel('Время выполнения, мс')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.savefig('graph.png', dpi=150)
plt.show()

print("График сохранён в graph.png")