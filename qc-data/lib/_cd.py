#!/usr/bin/env python3
from contextlib import contextmanager
import os
from os import path

@contextmanager
def _cd(dir):
    prev_dir = os.getcwd()
    os.chdir(path.expanduser(dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)
