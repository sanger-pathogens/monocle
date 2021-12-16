import logging
from pathlib import PurePath
from subprocess import check_output
from zipfile import ZipFile, ZIP_DEFLATED

CURRENT_FOLDER = '.'
ENCODING_UTF_8 = 'UTF-8'
FORMAT_NUMBER_TO_FILE_SIZE_CLI = ['numfmt', '--to=iec', '--suffix=B']
WRITE_MODE = 'w'
# From 0 (fastest) to 9 (most compact). See https://docs.python.org/3/library/zlib.html#zlib.compressobj
# Going above lvl 1 gains us little while increasing the compression time significantly (esp. when reads are included).
# Note: when changing this constant, update `ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS` in `sample_data_services.py` accordingly.
ZIP_COMPRESSION_LEVEL = 0
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
  zfile_full_name = PurePath(location) / zfile_name
  with injected_zip_file_lib(
    zfile_full_name,
    mode=WRITE_MODE,
    compression=ZIP_DEFLATED,
    compresslevel=ZIP_COMPRESSION_LEVEL) as zfile:
    for dir_name, files in dir_name_to_files.items():
      for this_file in files:
        try:
          zfile.write(this_file, PurePath(dir_name, this_file.name))
        except FileNotFoundError:
          logging.debug(f'Excluding non-existent file from download: {this_file}')
