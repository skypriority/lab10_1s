"""Итерация 5*. Оценка целесообразности примитивов синхронизации
(семафор, мьютекс) для задачи integrate_async.

Демонстрация: у каждого потока/задачи — СВОЙ локальный аккумулятор acc,
общих изменяемых данных между потоками нет, результаты складываются
только после f.result() в главном потоке. Поэтому семафор/мьютекс
здесь не нужны в принципе — гонки данных отсутствуют по конструкции
задачи. Ниже показано, что искусственное добавление мьютекса вокруг
общего аккумулятора не меняет корректность, но снижает
производительность (сериализует то, что и так не было бы гонкой).
"""

import threading
import time
from typing import Callable


def integrate_shared_no_lock(f: Callable[[float], float], a: float, b: float, *, n_jobs: int = 4,
                              n_iter: int = 10 ** 5) -> float:
    """Вариант с ОБЩИМ аккумулятором и БЕЗ синхронизации (для демонстрации гонки)."""
    acc = [0.0]
    step_outer = (b - a) / n_jobs
    step_inner_iter = n_iter // n_jobs

    def worker(lo: float, hi: float) -> None:
        local_step = (hi - lo) / step_inner_iter
        s = 0.0
        for i in range(step_inner_iter):
            s += f(lo + i * local_step) * local_step
        acc[0] += s

    threads = [
        threading.Thread(target=worker, args=(a + i * step_outer, a + (i + 1) * step_outer))
        for i in range(n_jobs)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return acc[0]


def integrate_shared_with_lock(f: Callable[[float], float], a: float, b: float, *, n_jobs: int = 4,
                                n_iter: int = 10 ** 5) -> float:
    """Тот же вариант, но обновление общего аккумулятора защищено мьютексом (Lock)."""
    acc = [0.0]
    lock = threading.Lock()
    step_outer = (b - a) / n_jobs
    step_inner_iter = n_iter // n_jobs

    def worker(lo: float, hi: float) -> None:
        local_step = (hi - lo) / step_inner_iter
        s = 0.0
        for i in range(step_inner_iter):
            s += f(lo + i * local_step) * local_step
        with lock:
            acc[0] += s

    threads = [
        threading.Thread(target=worker, args=(a + i * step_outer, a + (i + 1) * step_outer))
        for i in range(n_jobs)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return acc[0]


if __name__ == "__main__":
    import math

    r1 = integrate_shared_no_lock(math.sin, 0, math.pi, n_jobs=4, n_iter=400000)
    r2 = integrate_shared_with_lock(math.sin, 0, math.pi, n_jobs=4, n_iter=400000)
    print("без Lock:", r1)
    print("c Lock  :", r2)
    print(
        "\nВЫВОД: в исходной задаче integrate_async аккумулятор НЕ разделяется между\n"
        "потоками (каждый future возвращает свой результат, суммирование идёт в\n"
        "главном потоке после завершения задач) — поэтому семафор/мьютекс не нужны:\n"
        "нет общих изменяемых данных, значит нет и гонки. Примитивы синхронизации\n"
        "требуются только если сами воркеры пишут в ОБЩУЮ структуру данных (как в\n"
        "integrate_shared_with_lock выше) — и даже тогда это имеет смысл лишь при\n"
        "реальном параллелизме (nogil/free-threaded сборка или процессы), т.к. при\n"
        "включённом GIL операция acc[0] += s в CPython для float неатомарна на\n"
        "уровне байткода, но GIL и так сериализует байткод-инструкции, снижая (хотя\n"
        "не отменяя полностью) риск гонки; при отключённом GIL (free-threaded)\n"
        "гонка становится реальной, и Lock обязателен для корректности."
    )
