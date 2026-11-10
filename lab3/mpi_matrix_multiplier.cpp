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