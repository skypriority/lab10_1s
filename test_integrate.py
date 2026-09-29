"""Юнит-тесты для функции integrate() (итерация 1)."""

import math
import unittest

from integrate import integrate


class TestIntegrate(unittest.TestCase):
    """Проверка корректности численного интегрирования методом прямоугольников."""

    def test_known_integral_sin(self) -> None:
        """Интеграл sin(x) от 0 до pi должен быть близок к 2."""
        result = integrate(math.sin, 0, math.pi, n_iter=200000)
        self.assertAlmostEqual(result, 2.0, places=3)

    def test_known_integral_polynomial(self) -> None:
        """Интеграл x**2 от 0 до 1 должен быть близок к 1/3."""
        result = integrate(lambda x: x ** 2, 0, 1, n_iter=200000)
        self.assertAlmostEqual(result, 1 / 3, places=4)

    def test_stability_with_increasing_iterations(self) -> None:
        """С ростом n_iter результат должен сходиться к точному значению.

        Проверяем, что погрешность при n_iter=10**6 меньше погрешности
        при n_iter=10**3 (то есть метод устойчиво сходится).
        """
        exact = 2.0
        coarse = integrate(math.sin, 0, math.pi, n_iter=1000)
        fine = integrate(math.sin, 0, math.pi, n_iter=1000000)
        self.assertLess(abs(fine - exact), abs(coarse - exact))

    def test_zero_width_interval(self) -> None:
        """Интеграл по вырожденному отрезку [a, a] равен нулю."""
        result = integrate(math.cos, 1.0, 1.0, n_iter=100)
        self.assertAlmostEqual(result, 0.0, places=10)


if __name__ == "__main__":
    unittest.main()
