import logging
from pathlib import Path
from zipfile import ZipFile, ZIP_LZMA

CURRENT_FOLDER = '.'
WRITE_MODE = 'w'
ZIP_SUFFIX = '.zip'

def zip_files(files, *, basename, location=CURRENT_FOLDER, ZipFileInjected=ZipFile):
  if not files:
    logging.warning('no files passed')
    return

  zfile_name = basename + ZIP_SUFFIX
  zfile_full_name = Path(location) / zfile_name
  with ZipFileInjected(zfile_full_name, mode=WRITE_MODE, compression=ZIP_LZMA) as zfile:
    for file in files:
      zfile.write(file)
