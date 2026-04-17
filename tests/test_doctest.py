import os
import subprocess
import sys


def test_doctest_all():
    root = os.path.normpath(f'{__file__}/../../')
    subprocess.run(f'pip install --upgrade swig', shell=1, check=1)
    subprocess.run(f'cd {root} && {sys.executable} -m doctest -f -v src/pipcl.py', shell=1, check=1)


def _test_doctest_1():
    root = os.path.normpath(f'{__file__}/../../')
    subprocess.run(f'pip install --upgrade swig', shell=1, check=1)
    command = f'cd {root} && {sys.executable} src/pipcl.py --doctest _run_if_test_scripting_windows'
    print(f'\ntest_doctest1(): running {command=}.', flush=1)
    subprocess.run(command, shell=1, check=1)
