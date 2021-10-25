import logging
from pathlib import Path, PurePath
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

def zip_files(dir_name_to_files, *, basename, location=CURRENT_FOLDER, injected_zip_file_lib=ZipFile):
  no_files = not dir_name_to_files or all(
    len(lane_files) == 0 for lane_files in dir_name_to_files.values() )
  if no_files:
    logging.info('No files passed. Creating an empty zip archive.')

  zfile_name = basename + ZIP_SUFFIX
  zfile_full_name = Path(location) / zfile_name
  with injected_zip_file_lib(zfile_full_name, mode=WRITE_MODE, compression=ZIP_LZMA) as zfile:
    for dir_name, files in dir_name_to_files.items():
      for file in files:
        if Path(file).exists():
          zfile.write(file, PurePath(dir_name, file))
        else:
          logging.debug(f'Excluding non-exitent file from download: {file}')
