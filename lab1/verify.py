import numpy as np

BASE = "C:/Users/Софья/OneDrive/Desktop/parallel-programming/lab1/"

def read_matrix(filename):
    with open(filename, "r") as f:
        n = int(f.readline().strip())
        rows = [list(map(int, f.readline().split())) for _ in range(n)]
    return np.array(rows)

A = read_matrix(BASE + "matrix1.txt")
B = read_matrix(BASE + "matrix2.txt")
C_my = read_matrix(BASE + "result.txt")

C_etalon = np.dot(A, B)

if np.array_equal(C_my, C_etalon):
    print("Верификация пройдена: результаты C++ и NumPy совпадают.")
else:
    diff = np.abs(C_my - C_etalon)
    print(" ОШИБКА: результаты не совпадают!")
    print(f"Максимальное расхождение: {diff.max()}")
    print(f"Несовпадающих элементов: {np.count_nonzero(diff)}")