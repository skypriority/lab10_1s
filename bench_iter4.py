"""Итерация 4. Сравнение чистого Python и сайтонизированной версии integrate().

Требует предварительной сборки: python setup_cython.py build_ext --inplace
"""

import timeit

from integrate import integrate
from integrate_cython import integrate_cython


def compare() -> None:
    """Сравнить время выполнения обычной и cython-версии integrate()."""
    f = lambda x: x ** 2  # noqa: E731
    args = (f, 0, 1)
    kwargs = {"n_iter": 10 ** 6}

    assert abs(integrate(*args, **kwargs) - integrate_cython(*args, **kwargs)) < 1e-9

    t_py = timeit.timeit(lambda: integrate(*args, **kwargs), number=50)
    t_cy = timeit.timeit(lambda: integrate_cython(*args, **kwargs), number=50)

    print(f"Чистый Python : {t_py / 50 * 1000:8.3f} мс/вызов")
    print(f"Cython        : {t_cy / 50 * 1000:8.3f} мс/вызов")
    print(f"Ускорение     : {t_py / t_cy:.2f}x")


if __name__ == "__main__":
    compare()
