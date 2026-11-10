# Лабораторная работа №3
## Задание:
Модифицировать последовательную программу умножения матриц (из ЛР №1) для параллельной работы по технологии MPI. Провести серию экспериментов с разными размерами матриц и разным количеством вычислительных ядер на суперкомпьютере Самарского университета «Сергей Королёв».

## Описание:
Программа на C++ для параллельного перемножения двух квадратных матриц N × N классическим методом (тройной вложенный цикл) с использованием технологии MPI. Входные данные читаются из текстовых файлов, результат записывается в файл, замеряется время выполнения. Корректность результата проверяется автоматически с помощью библиотеки NumPy (максимальное отклонение = 0).

## Проект:

| Файл                     | Назначение                                    |
|--------------------------|-----------------------------------------------|
| `mpi_matrix_multiplier.cpp` | Параллельное перемножение матриц (MPI)      |
| `generate_matrices.py`   | Генерация двух случайных матриц `N x N`       |
| `build_plot.py`          | Построение графика                            |
| `verify.py`              | Автоматическая верификация через NumPy        |
| `CMakeLists.txt`         | Конфигурация сборки CMake с MPI               |
| `run_experiments.sl`     | Slurm-скрипт для запуска серии на кластере    |
| `matrix1.txt`            | Первая входная матрица (генерируется)         |
| `matrix2.txt`            | Вторая входная матрица (генерируется)         |
| `result.txt`             | Результат перемножения                        |
| `timings.txt`            | Результаты замеров времени                    |
| `graph.png`              | График зависимости времени от N               |

## Параллельная реализация:

### Ключевой фрагмент mpi_matrix_multiplier.cpp:
```cpp
#include <mpi.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int N = 0;
    std::vector<int> A, B, BT, C;
    int rows_per_proc = 0;

    if (rank == 0) {
        std::ifstream f1("matrix1.txt");
        std::ifstream f2("matrix2.txt");
        if (!f1.is_open() || !f2.is_open()) {
            std::cerr << "ОШИБКА! Не удалось открыть matrix1.txt или matrix2.txt\n";
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        f1 >> N;
        f2 >> N;

        if (N % size != 0) {
            std::cerr << "ОШИБКА! N=" << N << " не делится на число процессов " << size << "\n";
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        A.resize(N * N);
        B.resize(N * N);
        for (int i = 0; i < N; ++i)
            for (int j = 0; j < N; ++j)
                f1 >> A[i * N + j];
        for (int i = 0; i < N; ++i)
            for (int j = 0; j < N; ++j)
                f2 >> B[i * N + j];
    }

    MPI_Bcast(&N, 1, MPI_INT, 0, MPI_COMM_WORLD);
    rows_per_proc = N / size;

    if (rank != 0) {
        B.resize(N * N);
    }

    MPI_Bcast(B.data(), N * N, MPI_INT, 0, MPI_COMM_WORLD);

    BT.resize(N * N);
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j)
            BT[j * N + i] = B[i * N + j];

    std::vector<int> localA(rows_per_proc * N);
    MPI_Scatter(A.data(), rows_per_proc * N, MPI_INT,
                localA.data(), rows_per_proc * N, MPI_INT,
                0, MPI_COMM_WORLD);

    std::vector<int> localC(rows_per_proc * N, 0);
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < rows_per_proc; ++i) {
        for (int j = 0; j < N; ++j) {
            int sum = 0;
            for (int k = 0; k < N; ++k)
                sum += localA[i * N + k] * BT[j * N + k];
            localC[i * N + j] = sum;
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    long long local_ms = duration.count();

    if (rank == 0) C.resize(N * N);
    MPI_Gather(localC.data(), rows_per_proc * N, MPI_INT,
               C.data(), rows_per_proc * N, MPI_INT,
               0, MPI_COMM_WORLD);

    if (rank == 0) {
        std::ofstream out("result.txt");
        out << N << '\n';
        for (int i = 0; i < N; ++i) {
            for (int j = 0; j < N; ++j)
                out << C[i * N + j] << ' ';
            out << '\n';
        }
        out.close();
    }

    long long global_ms = 0;
    MPI_Reduce(&local_ms, &global_ms, 1, MPI_LONG_LONG, MPI_MAX, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        std::cout << N << "," << global_ms << std::endl;
    }

    MPI_Finalize();
    return 0;
}
```

## Сборка и запуск:
### На суперкомпьютере «Сергей Королёв» (Slurm):

```bash
sbatch run_experiments.sl
```

## Построение графиков:
```cmd
python build_plot.py
```

## Результаты:

### Исходные данные для графиков

| N     | T = 1      | T = 2      | T = 4      | T = 8      |
|-------|------------|------------|------------|------------|
| 200   | 8.33 мс    | 4.00 мс    | 2.00 мс    | 1.00 мс    |
| 400   | 68.00 мс   | 33.67 мс   | 16.00 мс   | 8.00 мс    |
| 800   | 534.00 мс  | 267.00 мс  | 134.33 мс  | 68.33 мс   |
| 1200  | 1791.33 мс | 896.00 мс  | 461.33 мс  | 246.00 мс  |
| 1600  | 3991.33 мс | 2116.33 мс | 1139.67 мс | 583.33 мс  |
| 2000  | 8004.33 мс | 4122.67 мс | 2136.00 мс | 1138.33 мс |

### График зависимости

[График](graph.png)

## Верификация результата

Запуск:
```bash
python verify.py
```

Скрипт сравнивает `result.txt` с эталонным результатом, полученным через
`numpy.dot(A, B)`, и выводит:
```
Верификация пройдена: результаты C++ и NumPy совпадают.
```
либо сообщает о расхождениях.

# Вывод:
В рамках лабораторной работы была реализована параллельная версия программы умножения квадратных матриц на языке C++ с использованием технологии MPI. Экспериментально исследована зависимость времени выполнения от размера матрицы и количества процессов. Установлено, что ускорение растёт с числом процессов, приближаясь к линейному для больших матриц. Результаты вычислений подтверждены автоматической верификацией с помощью NumPy.
