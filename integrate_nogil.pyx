"""Итерация 5. Cython-версия integrate() с освобождением GIL (nogil).

Функцию ``f`` вызывать без GIL нельзя (это произвольный Python-объект),
поэтому GIL освобождается только вокруг чисто C-арифметики цикла —
для честного сравнения с чистым Python-циклом реализован также вариант
integrate_cython_c, интегрирующий C-функцию (math.cos через libm),
которую можно вызвать полностью без GIL.

Компилировать: python setup_cython_nogil.py build_ext --inplace
"""

from libc.math cimport cos as c_cos

cimport cython


@cython.boundscheck(False)
@cython.wraparound(False)
def integrate_cython(f, double a, double b, *, int n_iter=1000):
    """Сайтонизированная версия integrate() (см. integrate_cython.pyx)."""
    cdef double acc = 0.0
    cdef double step = (b - a) / n_iter
    cdef int i
    for i in range(n_iter):
        acc += f(a + i * step) * step
    return acc


@cython.boundscheck(False)
@cython.wraparound(False)
def integrate_cos_nogil(double a, double b, *, int n_iter=1000):
    """Интеграл cos(x) на [a, b], полностью считаемый без GIL.

    В отличие от :func:`integrate_cython`, здесь интегрируемая функция —
    не произвольный Python-объект, а функция C-библиотеки ``libm``
    (``cos`` из ``libc.math``), поэтому весь цикл можно выполнить в блоке
    ``with nogil``, реально освобождая GIL на всё время вычисления. Это
    даёт возможность нескольким потокам считать параллельно на разных
    ядрах CPU без взаимной блокировки.

    :param a: нижний предел интегрирования.
    :param b: верхний предел интегрирования.
    :param n_iter: количество разбиений отрезка ``[a, b]``.
    :return: приближённое значение интеграла cos(x) на отрезке ``[a, b]``.
    """
    cdef double acc = 0.0
    cdef double step = (b - a) / n_iter
    cdef int i
    with nogil:
        for i in range(n_iter):
            acc += c_cos(a + i * step) * step
    return acc
