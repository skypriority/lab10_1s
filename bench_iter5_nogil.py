# -*- coding: utf-8 -*-
"""Итерация 5. Замер ускорения потоков на функции integrate_cos_nogil
(интеграл считается в C-коде с освобождённым GIL) при 2, 4, 6, 8 потоках.

Запускать ОБЯЗАТЕЛЬНО из venv313t (free-threaded интерпретатор), где GIL
по умолчанию отключён (PYTHON_GIL=0), чтобы потоки реально работали
параллельно. Тот же скрипт можно запустить из обычного venv313 (GIL
включён) для сравнения "до/после".
"""

import concurrent.futures as ftres
import sys
import timeit

from integrate_nogil import integrate_cos_nogil


def integrate_threads_nogil(a: float, b: float, *, n_jobs: int = 2, n_iter: int = 10 ** 6) -> float:
    """Посчитать интеграл cos(x) параллельно в потоках, используя nogil-функцию."""
    step = (b - a) / n_jobs
    with ftres.ThreadPoolExecutor(max_workers=n_jobs) as executor:
        fs = [
            executor.submit(integrate_cos_nogil, a + i * step, a + (i + 1) * step, n_iter=n_iter // n_jobs)
            for i in range(n_jobs)
        ]
        return sum(f.result() for f in ftres.as_completed(fs))


def main() -> None:
    """Провести замеры и вывести сводку."""
    gil_status = "выключен (free-threaded)" if not sys._is_gil_enabled() else "включён"
    print(f"Интерпретатор: {sys.version.splitlines()[0]}")
    print(f"GIL: {gil_status}\n")

    a, b = 0.0, 3.14159265358979
    n_iter = 10 ** 7

    baseline = timeit.timeit(lambda: integrate_threads_nogil(a, b, n_jobs=1, n_iter=n_iter), number=5) / 5
    print(f"n_jobs=1 (базовый): {baseline * 1000:8.3f} мс")

    for n_jobs in (2, 4, 6, 8):
        t = timeit.timeit(lambda: integrate_threads_nogil(a, b, n_jobs=n_jobs, n_iter=n_iter), number=5) / 5
        print(f"n_jobs={n_jobs}: {t * 1000:8.3f} мс   ускорение x{baseline / t:.2f}")


if __name__ == "__main__":
    main()
