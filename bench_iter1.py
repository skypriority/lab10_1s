import math
import timeit

from integrate import integrate


def measure() -> None:
    """Провести серию замеров времени работы integrate() для разного n_iter."""
    args = (math.cos, 0, math.pi / 2)
    for n_iter in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6):
        t = timeit.timeit(
            lambda: integrate(*args, n_iter=n_iter),
            number=20,
        )
        avg_ms = t / 20 * 1000
        print(f"n_iter={n_iter:>8}: {avg_ms:8.3f} мс/вызов (суммарно {t:.3f} с за 20 запусков)")


if __name__ == "__main__":
    measure()
