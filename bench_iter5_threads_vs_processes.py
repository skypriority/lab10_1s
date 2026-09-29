# -*- coding: utf-8 -*-
"""Итерация 5 (продолжение). Сравнение: потоки без GIL (Cython nogil,
free-threaded интерпретатор) против процессов на сайтонизированной версии.
"""

import concurrent.futures as ftres
import math
import sys
import timeit

from integrate_nogil import integrate_cos_nogil


def integrate_process_cython(a: float, b: float, *, n_jobs: int = 2, n_iter: int = 10 ** 6) -> float:
    """Посчитать интеграл cos(x) в процессах, вызывая cython-функцию integrate_cos_nogil."""
    step = (b - a) / n_jobs
    with ftres.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        fs = [
            executor.submit(integrate_cos_nogil, a + i * step, a + (i + 1) * step, n_iter=n_iter // n_jobs)
            for i in range(n_jobs)
        ]
        return sum(f.result() for f in ftres.as_completed(fs))


def integrate_threads_nogil(a: float, b: float, *, n_jobs: int = 2, n_iter: int = 10 ** 6) -> float:
    """Посчитать интеграл cos(x) в потоках, вызывая cython-функцию integrate_cos_nogil."""
    step = (b - a) / n_jobs
    with ftres.ThreadPoolExecutor(max_workers=n_jobs) as executor:
        fs = [
            executor.submit(integrate_cos_nogil, a + i * step, a + (i + 1) * step, n_iter=n_iter // n_jobs)
            for i in range(n_jobs)
        ]
        return sum(f.result() for f in ftres.as_completed(fs))


def main() -> None:
    """Сравнить потоки (nogil) и процессы на одинаковой cython-функции."""
    gil_status = "выключен" if not sys._is_gil_enabled() else "включён"
    print(f"Интерпретатор: {sys.version.splitlines()[0]}, GIL: {gil_status}\n")

    a, b, n_iter = 0.0, math.pi, 10 ** 7

    for n_jobs in (2, 4, 6, 8):
        t_threads = timeit.timeit(
            lambda: integrate_threads_nogil(a, b, n_jobs=n_jobs, n_iter=n_iter), number=5
        ) / 5
        t_proc = timeit.timeit(
            lambda: integrate_process_cython(a, b, n_jobs=n_jobs, n_iter=n_iter), number=5
        ) / 5
        print(
            f"n_jobs={n_jobs}: потоки(nogil)={t_threads * 1000:8.3f} мс   "
            f"процессы={t_proc * 1000:8.3f} мс"
        )


if __name__ == "__main__":
    main()
