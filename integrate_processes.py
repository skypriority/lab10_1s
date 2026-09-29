# -*- coding: utf-8 -*-
"""Итерация 3. Оптимизация вычисления интеграла с помощью процессов (multiprocessing).

Функция для параллельного вычисления должна быть импортируемой на верхнем
уровне модуля (а не lambda и не вложенной функцией), т.к. ProcessPoolExecutor
на Windows использует spawn и пиклит (pickle) передаваемые объекты, включая
саму функцию ``f``.
"""

import concurrent.futures as ftres
from functools import partial
from typing import Callable

from integrate import integrate


def integrate_process(
    f: Callable[[float], float],
    a: float,
    b: float,
    *,
    n_jobs: int = 2,
    n_iter: int = 1000,
) -> float:
    """Вычислить интеграл параллельно, используя пул процессов.

    Аналог :func:`integrate_threads.integrate_async`, но вместо потоков
    задачи выполняются в отдельных процессах (``ProcessPoolExecutor``),
    что позволяет обойти ограничение GIL и добиться реального параллелизма
    на CPU-bound вычислениях — ценой накладных расходов на межпроцессное
    взаимодействие (создание процессов, сериализация аргументов и
    результатов через pickle).

    :param f: интегрируемая функция одной вещественной переменной. Должна
        быть импортируемой (picklable) — например, определена на уровне
        модуля, а не lambda.
    :param a: нижний предел интегрирования.
    :param b: верхний предел интегрирования.
    :param n_jobs: количество процессов (и подотрезков разбиения).
    :param n_iter: суммарное число разбиений на прямоугольники, поровну
        распределяется между процессами.
    :return: приближённое значение интеграла ``f`` на отрезке ``[a, b]``.
    :raises ZeroDivisionError: если ``n_jobs == 0``.
    """
    with ftres.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        spawn = partial(executor.submit, integrate, f, n_iter=n_iter // n_jobs)
        step = (b - a) / n_jobs
        fs = [spawn(a + i * step, a + (i + 1) * step) for i in range(n_jobs)]
        result = sum(fut.result() for fut in ftres.as_completed(fs))
    return result


if __name__ == "__main__":
    import math

    print(integrate_process(math.sin, 0, math.pi))
