#!/usr/bin/env python3
from pathlib import Path
import logging

def _mkdir(dir_name):
    if Path(dir_name).is_dir():
        logging.debug(f'Directory {dir_name} already exists in {Path().absolute()}.')
    else:
        Path(dir_name).mkdir()
        logging.info(f'Directory {dir_name} was created at {Path().absolute()}.')
