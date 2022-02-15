from unittest      import TestCase
from unittest.mock import create_autospec, patch, Mock
from functools     import reduce
from pathlib       import Path, PurePath
from zipfile       import ZipFile, ZIP_DEFLATED

from utils.file    import format_file_size, zip_files, ZIP_COMPRESSION_LEVEL, WRITE_MODE, complete_zipfile

PUBLIC_NAME_TO_LANE_FILES = {
  'pub_name_1': [PurePath('a_file.txt'), PurePath('another_file.fastq')],
  'pub_name_2': [PurePath('some_other_file.txt'), PurePath('yet_another_file.fastq')]
}
BASENAME = 'batches'
ZIP_FILE_NAME = BASENAME + '.zip'

GOOD_ZIP_FILE     = 'dash/tests/mock_data/zip/good.zip'
MANGLED_ZIP_FILE  = 'dash/tests/mock_data/zip/mangled.zip'
EMPTY_ZIP_FILE    = 'dash/tests/mock_data/zip/empty.zip'

class TestFileUtil(TestCase):

  ZipFileMock = create_autospec(ZipFile)

  def tearDown(self):
    self.ZipFileMock.reset_mock()

  def test_format_file_size_by_calling_correct_cli_program(self):
    bytes = 9499499443
    call_cli = Mock()

    format_file_size(bytes, call_cli)

    call_cli.assert_called_once_with(
      ['numfmt', '--to=iec', '--suffix=B', str(bytes)],
      encoding='UTF-8')

  def test_format_file_size_strips_newlines_and_spaces_from_the_end(self):
    call_cli = Mock()
    expected = '3 TB'
    call_cli.return_value = f'{expected} \n\n'

    actual = format_file_size(123, call_cli)

    self.assertEqual(actual, expected)

  def test_format_file_size_returns_bytes_as_string_if_calling_cli_fails(self):
    bytes = 9499499443
    call_cli = Mock()
    call_cli.side_effect = Exception('some error')

    actual = format_file_size(bytes, call_cli)

    self.assertEqual(actual, f'{bytes} B')

  def test_zip_files(self):
    zipfile_instance = self.ZipFileMock.return_value
    # Make the instance of `ZipFileMock` available in the context manager of `zip_files()`.
    zipfile_instance.__enter__.return_value = zipfile_instance
    location = 'downloads'

    zip_files(PUBLIC_NAME_TO_LANE_FILES,
      basename=BASENAME,
      location=location,
      injected_zip_file_lib=self.ZipFileMock)

    expected_zip_file_full_name = PurePath(location) / ZIP_FILE_NAME
    self.ZipFileMock.assert_called_once_with(
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_DEFLATED, compresslevel=ZIP_COMPRESSION_LEVEL)
    num_files = reduce(
      lambda accum, lane_files: accum + len(lane_files),
      PUBLIC_NAME_TO_LANE_FILES.values(),
      0)
    self.assertEqual(zipfile_instance.write.call_count, num_files)
    for public_name, files in PUBLIC_NAME_TO_LANE_FILES.items():
      for file in files:
        zipfile_instance.write.assert_any_call(
          file, PurePath(public_name, file.name))

  def test_zip_files_works_with_nonexistent_files(self):
    zipfile_instance = self.ZipFileMock.return_value
    # Make the instance of `ZipFileMock` available in the context manager of `zip_files()`.
    zipfile_instance.__enter__.return_value = zipfile_instance

    zip_files(PUBLIC_NAME_TO_LANE_FILES, basename=BASENAME, injected_zip_file_lib=self.ZipFileMock)

    expected_zip_file_full_name = PurePath('.') / ZIP_FILE_NAME
    self.ZipFileMock.assert_called_once_with(
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_DEFLATED, compresslevel=ZIP_COMPRESSION_LEVEL)
    num_files = 4
    zipfile_instance.write('non-existent.file')
    self.assertEqual(zipfile_instance.write.call_count, num_files + 1)

  def test_zip_files_to_current_folder_if_no_location_given(self):
    zip_files(PUBLIC_NAME_TO_LANE_FILES, basename=BASENAME, injected_zip_file_lib=self.ZipFileMock)

    expected_zip_file_full_name = PurePath('.') / ZIP_FILE_NAME
    self.ZipFileMock.assert_called_once_with(
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_DEFLATED, compresslevel=ZIP_COMPRESSION_LEVEL)

  def test_zip_files_creates_empty_archive_if_no_files_passed(self):
    zip_files({}, basename=BASENAME, injected_zip_file_lib=self.ZipFileMock)

    expected_zip_file_full_name = PurePath('.') / ZIP_FILE_NAME
    # Instantiating `ZipFile` creates an empty ZIP archive even if `write()` isn't called.
    self.ZipFileMock.assert_called_once_with(
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_DEFLATED, compresslevel=ZIP_COMPRESSION_LEVEL)
    
  def test_complete_zipfile(self):
    self.assertTrue(  complete_zipfile(GOOD_ZIP_FILE)    )
    self.assertFalse( complete_zipfile(MANGLED_ZIP_FILE) )
    self.assertFalse( complete_zipfile(EMPTY_ZIP_FILE)   )
