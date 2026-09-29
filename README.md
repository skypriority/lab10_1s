# Лабораторная работа 10. Методы оптимизации вычисления кода (потоки, процессы, Cython, отпускание GIL)

Цель работы: исследовать методы оптимизации вычисления кода, используя
потоки, процессы, Cython и отключение GIL, на примере функции численного
интегрирования методом левых прямоугольников, реализованной на чистом
Python.

Все результаты в этом репозитории — реальные замеры, полученные запуском
кода локально (Windows, CPython 3.11.16 / 3.13.15 / 3.13.15 free-threaded /
3.14.0, GCC 16.2.0 MinGW-w64, 28 логических ядер CPU). Полный разбор с
таблицами и выводами по каждой итерации — в [`REPORT.md`](REPORT.md).

## Структура репозитория

| Файл | Итерация | Назначение |
|---|---|---|
| `integrate.py` | 1 | Базовая реализация `integrate()`: docstring (PEP 257), аннотации типов (PEP 484), 2 doctest-примера |
| `test_integrate.py` | 1 | Юнит-тесты (`unittest`): известные интегралы, устойчивость к росту `n_iter`, граничный случай |
| `bench_iter1.py` | 1 | Замеры `timeit` для разных `n_iter` |
| `integrate_threads.py` | 2 | `integrate_async()` на `ThreadPoolExecutor` |
| `integrate_processes.py` | 3 | `integrate_process()` на `ProcessPoolExecutor` |
| `bench_iter23.py` | 2-3 | Сравнение времени при `n_jobs = 1, 2, 4, 6, 8` |
| `profile_integrate.py` | 4 | Профилирование `cProfile` |
| `integrate_cython.pyx`, `setup_cython.py`, `integrate_cython.html` | 4 | Сайтонизированная версия + HTML-аннотация |
| `bench_iter4.py` | 4 | Сравнение чистый Python vs Cython |
| `integrate_nogil.pyx`, `setup_cython_nogil.py`, `integrate_nogil.html` | 5 | Cython-версия с `with nogil` |
| `bench_iter5_nogil.py` | 5 | Ускорение потоков на nogil-функции (обычный GIL и free-threaded) |
| `bench_iter5_threads_vs_processes.py` | 5 | Потоки (nogil) против процессов |
| `sync_primitives_demo.py` | 5* | Нужны ли мьютекс/семафор для этой задачи |

## Как запустить

Требуется несколько интерпретаторов CPython (обычный, и опционально
free-threaded для итерации 5) и GCC для сборки Cython-расширений.

```bash
# итерация 1
python -m unittest test_integrate -v
python -m doctest integrate.py -v
python bench_iter1.py

# итерации 2-3 (потоки/процессы)
python bench_iter23.py

# итерация 4 (нужны собранные .pyd-модули, см. ниже)
python profile_integrate.py
python bench_iter4.py

# итерация 5 (желателен free-threaded интерпретатор, PYTHON_GIL=0)
python bench_iter5_nogil.py
python bench_iter5_threads_vs_processes.py
python sync_primitives_demo.py
```

### Сборка Cython-расширений (Windows)

Cython требует C-компилятор в PATH (на Windows не идёт из коробки, в отличие
от Colab/Linux). Пример с MinGW-w64:

```bash
pip install cython setuptools
python setup_cython.py build_ext --inplace --compiler=mingw32
python setup_cython_nogil.py build_ext --inplace --compiler=mingw32
```

### Free-threaded интерпретатор (для честных замеров nogil)

```bash
uv python install cpython-3.13.15+freethreaded-windows-x86_64-none
PYTHON_GIL=0 python3.13t bench_iter5_nogil.py
```

## Главные выводы (кратко)

1. Потоки на чистом Python не ускоряют CPU-bound код — мешает GIL. Проверено
   на 3.11, 3.13 и 3.14 (обычная сборка) — везде одинаковая картина: рост
   `n_jobs` выше 2 не даёт ускорения.
2. Процессы дают реальный параллелизм, но при лёгких задачах накладные
   расходы IPC (создание процессов, pickle) перевешивают выигрыш.
3. Типизация переменных в Cython (`cdef double/int`) почти не ускоряет код,
   пока сам вызов интегрируемой функции `f()` идёт через Python C-API —
   именно он, а не арифметика цикла, доминирует по времени.
4. Явное освобождение GIL в Cython (`with nogil`) при интегрировании
   C-функции (`libc.math.cos`) даёт честное многопоточное ускорение
   (до ~4.6x на 8 потоках) даже на обычной сборке CPython.
5. Free-threaded интерпретатор (3.13, `PYTHON_GIL=0`) даёт дополнительный
   выигрыш поверх nogil-Cython (до ~5.4x на 8 потоках).
6. Примитивы синхронизации (мьютекс/семафор) в данной задаче не нужны —
   каждый воркер возвращает независимый результат через `Future`, общего
   изменяемого состояния между потоками/процессами нет.

Подробности, все таблицы с цифрами и объяснение «почему Cython-вариант в
Colab не быстрее и как это исправить» — см. [`REPORT.md`](REPORT.md).
