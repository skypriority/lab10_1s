"""Итерация 4. Профилирование чистой Python-версии integrate()."""

import cProfile
import math
import pstats

from integrate import integrate


def profile() -> None:
    """Профилировать integrate() с помощью cProfile и вывести топ строк."""
    profiler = cProfile.Profile()
    profiler.enable()
    integrate(math.cos, 0, math.pi / 2, n_iter=10 ** 6)
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(10)


if __name__ == "__main__":
    profile()
