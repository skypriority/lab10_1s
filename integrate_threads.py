"""Итерация 2. Оптимизация вычисления интеграла с помощью потоков (threading)."""

import concurrent.futures as ftres
from functools import partial
from typing import Callable

from integrate import integrate


def integrate_async(
    f: Callable[[float], float],
    a: float,
    b: float,
    *,
    n_jobs: int = 2,
    n_iter: int = 1000,
) -> float:
    """Вычислить интеграл параллельно, разбив отрезок между потоками.

    Отрезок ``[a, b]`` делится на ``n_jobs`` равных подотрезков, каждый из
    которых считается функцией :func:`integrate` в отдельном потоке пула
    ``ThreadPoolExecutor``. Результаты суммируются по мере завершения задач.

    :param f: интегрируемая функция одной вещественной переменной.
    :param a: нижний предел интегрирования.
    :param b: верхний предел интегрирования.
    :param n_jobs: количество потоков (и подотрезков разбиения).
    :param n_iter: суммарное число разбиений на прямоугольники, будет
        поровну распределено между потоками (``n_iter // n_jobs`` на поток).
    :return: приближённое значение интеграла ``f`` на отрезке ``[a, b]``.
    :raises ZeroDivisionError: если ``n_jobs == 0``.

    .. note::
        Из-за GIL (Global Interpreter Lock) в стандартном CPython потоки
        не дают ускорения на CPU-bound задачах (см. итерация 2, вывод по
        замерам ниже) — байткод-инструкции разных потоков выполняются
        по очереди, а не параллельно.
    """
    executor = ftres.ThreadPoolExecutor(max_workers=n_jobs)
    spawn = partial(executor.submit, integrate, f, n_iter=n_iter // n_jobs)
    step = (b - a) / n_jobs
    fs = [spawn(a + i * step, a + (i + 1) * step) for i in range(n_jobs)]
    result = sum(fut.result() for fut in ftres.as_completed(fs))
    executor.shutdown(wait=True)
    return result


if __name__ == "__main__":
    import math

    print(integrate_async(math.sin, 0, math.pi))
