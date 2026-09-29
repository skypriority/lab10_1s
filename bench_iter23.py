"""Итерации 2-3. Замеры времени работы integrate_async (потоки) и
integrate_process (процессы) при n_jobs = 2, 4, 6, 8."""

import math
import timeit

from integrate_processes import integrate_process
from integrate_threads import integrate_async


def measure_threads() -> None:
    """Замерить время работы integrate_async при разном числе потоков."""
    print("=== Потоки (ThreadPoolExecutor) ===")
    args = (math.cos, 0, math.pi / 2)
    n_iter = 10 ** 5
    for n_jobs in (1, 2, 4, 6, 8):
        t = timeit.timeit(
            lambda: integrate_async(*args, n_jobs=n_jobs, n_iter=n_iter),
            number=10,
        )
        print(f"n_jobs={n_jobs}: {t / 10 * 1000:8.3f} мс/вызов")


def measure_processes() -> None:
    """Замерить время работы integrate_process при разном числе процессов."""
    print("=== Процессы (ProcessPoolExecutor) ===")
    args = (math.cos, 0, math.pi / 2)
    n_iter = 10 ** 5
    for n_jobs in (1, 2, 4, 6, 8):
        t = timeit.timeit(
            lambda: integrate_process(*args, n_jobs=n_jobs, n_iter=n_iter),
            number=10,
        )
        print(f"n_jobs={n_jobs}: {t / 10 * 1000:8.3f} мс/вызов")


if __name__ == "__main__":
    measure_threads()
    measure_processes()
