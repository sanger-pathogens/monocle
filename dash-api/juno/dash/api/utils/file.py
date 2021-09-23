import logging
from pathlib import Path
from subprocess import check_output
from zipfile import ZipFile, ZIP_LZMA

CURRENT_FOLDER = '.'
ENCODING_UTF_8 = 'UTF-8'
FORMAT_NUMBER_TO_FILE_SIZE_CLI = ['numfmt', '--to=iec', '--suffix=B']
WRITE_MODE = 'w'
ZIP_SUFFIX = '.zip'


def format_file_size(bytes, call_cli=check_output):
  try:
    return call_cli(
      [*FORMAT_NUMBER_TO_FILE_SIZE_CLI, str(bytes)],
      encoding=ENCODING_UTF_8
    ).rstrip()
  except BaseException as err:
    logging.error(f'Couldn\'t format argument `{bytes}` to file size: {err}')
    return f'{bytes} B'


def zip_files(files, *, basename, location=CURRENT_FOLDER, ZipFileInjected=ZipFile):
  if not files:
    logging.warning('no files passed')
    return

  zfile_name = basename + ZIP_SUFFIX
  zfile_full_name = Path(location) / zfile_name
  with ZipFileInjected(zfile_full_name, mode=WRITE_MODE, compression=ZIP_LZMA) as zfile:
    for file in files:
      zfile.write(file)
