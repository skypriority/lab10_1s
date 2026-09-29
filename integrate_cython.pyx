# cython: language_level=3
"""Итерация 4. Сайтонизированная версия integrate().

Компилировать: python setup_cython.py build_ext --inplace
"""

from typing import Callable

cimport cython


@cython.boundscheck(False)
@cython.wraparound(False)
def integrate_cython(f: Callable[[float], float], double a, double b, *, int n_iter=1000):
    """Вычислить интеграл методом левых прямоугольников (Cython-версия).

    Логика идентична :func:`integrate.integrate`, но переменные цикла и
    аккумулятор объявлены как типизированные C-переменные (``cdef double``,
    ``cdef int``), что убирает часть накладных расходов интерпретатора
    Python на арифметику и позволяет GCC сгенерировать более эффективный
    машинный код для цикла. Вызов самой функции ``f`` остаётся вызовом
    Python-объекта (через C-API), поэтому основной выигрыш в производительности
    даёт только цикл и арифметика вокруг него, а не сам вызов ``f``.

    :param f: интегрируемая функция одной вещественной переменной.
    :param a: нижний предел интегрирования.
    :param b: верхний предел интегрирования.
    :param n_iter: количество разбиений отрезка ``[a, b]``.
    :return: приближённое значение интеграла ``f`` на отрезке ``[a, b]``.
    """
    cdef double acc = 0.0
    cdef double step = (b - a) / n_iter
    cdef int i
    for i in range(n_iter):
        acc += f(a + i * step) * step
    return acc
