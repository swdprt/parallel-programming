#!/bin/bash
#PBS -N lab3_mpi
#PBS -l nodes=1:ppn=8
#PBS -l walltime=02:00:00
#PBS -j oe

cd $PBS_O_WORKDIR
module load impi/4

SIZES="200 400 800 1200 1600 2000"
PROCS="1 2 4 8"
REPEATS=3
TIMINGS="timings.txt"

echo "=== Компиляция ==="
mpicc -O2 -o mpi_mm mpi_matrix_multiplier.cpp -lstdc++
echo "OK"

echo "N,procs,time_ms" > $TIMINGS

for N in $SIZES; do
    echo "=== Генерация матриц N=$N ==="
    python3 generate_matrices.py $N

    for P in $PROCS; do
        if [ $((N % P)) -ne 0 ]; then
            echo "SKIP: N=$N не делится на P=$P"
            continue
        fi

        for R in $(seq 1 $REPEATS); do
            echo "Запуск: N=$N, procs=$P, повтор=$R"

            OUTPUT=$(mpirun -np $P ./mpi_mm)
            MS=$(echo "$OUTPUT" | tail -n 1 | cut -d',' -f2)

            if [ -z "$MS" ]; then
                echo "ОШИБКА: не удалось получить время (N=$N, P=$P, R=$R)"
                echo "Вывод программы: $OUTPUT"
                continue
            fi

            echo "$N,$P,$MS" >> $TIMINGS
        done
    done
done

echo "=== Готово. Результаты в $TIMINGS ==="
cat $TIMINGS