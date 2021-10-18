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


def zip_files(files, *, basename, location=CURRENT_FOLDER, injected_zip_file_lib=ZipFile, ignore_missing_files=False):
  if not files:
    logging.warning('no files passed')
    return

  files_to_zip = []
  if ignore_missing_files:
    for this_file in files:
      if Path(this_file).exists():
         files_to_zip.append(this_file)
         logging.info("file for download: {}".format(this_file))
      else:
         logging.debug("Excluding non-exitent file from download: {}".format(this_file))
  else:
    files_to_zip = files

  zfile_name = basename + ZIP_SUFFIX
  zfile_full_name = Path(location) / zfile_name
  with injected_zip_file_lib(zfile_full_name, mode=WRITE_MODE, compression=ZIP_LZMA) as zfile:
    for this_file in files_to_zip:
      zfile.write(this_file)
