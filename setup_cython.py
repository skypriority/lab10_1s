"""Сборка Cython-модуля integrate_cython."""

from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    ext_modules=cythonize(
        [Extension("integrate_cython", ["integrate_cython.pyx"])],
        annotate=True,
        compiler_directives={"language_level": "3"},
    ),
)
