"""Сборка Cython-модуля integrate_nogil (итерация 5)."""

from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    ext_modules=cythonize(
        [Extension("integrate_nogil", ["integrate_nogil.pyx"])],
        annotate=True,
        compiler_directives={"language_level": "3"},
    ),
)
