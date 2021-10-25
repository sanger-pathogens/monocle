from unittest      import TestCase
from unittest.mock import create_autospec, patch, Mock
from functools     import reduce
from pathlib       import Path, PurePath
from zipfile       import ZipFile, ZIP_LZMA

from utils.file import format_file_size, zip_files, WRITE_MODE

PUBLIC_NAME_TO_LANE_FILES = {
  'pub_name_1': ['a_file.txt', 'another_file.fastq'],
  'pub_name_2': ['some_other_file.txt', 'yet_another_file.fastq']
}
BASENAME = 'batches'
ZIP_FILE_NAME = BASENAME + '.zip'

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

  @patch.object(Path, 'exists', return_value=True)
  def test_zip_files(self, _file_exists_mock):
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
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_LZMA)
    num_files = reduce(
      lambda accum, lane_files: accum + len(lane_files),
      PUBLIC_NAME_TO_LANE_FILES.values(),
      0)
    self.assertEqual(zipfile_instance.write.call_count, num_files)
    for public_name, files in PUBLIC_NAME_TO_LANE_FILES.items():
      for file in files:
        zipfile_instance.write.assert_any_call(
          file, PurePath(public_name, file))

  def test_zip_files_ignores_missing_files(self):
    zipfile_instance = self.ZipFileMock.return_value
    # Make the instance of `ZipFileMock` available in the context manager of `zip_files()`.
    zipfile_instance.__enter__.return_value = zipfile_instance

    zip_files(PUBLIC_NAME_TO_LANE_FILES, basename=BASENAME, injected_zip_file_lib=self.ZipFileMock)

    expected_zip_file_full_name = PurePath('.') / ZIP_FILE_NAME
    self.ZipFileMock.assert_called_once_with(
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_LZMA)
    self.assertEqual(zipfile_instance.write.call_count, 0)

  @patch.object(Path, 'exists', return_value=True)
  def test_zip_files_to_current_folder_if_no_location_given(self, _file_exists_mock):
    zip_files(PUBLIC_NAME_TO_LANE_FILES, basename=BASENAME, injected_zip_file_lib=self.ZipFileMock)

    expected_zip_file_full_name = PurePath('.') / ZIP_FILE_NAME
    self.ZipFileMock.assert_called_once_with(
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_LZMA)

  def test_zip_files_creates_empty_archive_if_no_files_passed(self):
    zip_files({}, basename=BASENAME, injected_zip_file_lib=self.ZipFileMock)

    expected_zip_file_full_name = PurePath('.') / ZIP_FILE_NAME
    # Instantiating `ZipFile` creates an empty ZIP archive even if `write()` isn't called.
    self.ZipFileMock.assert_called_once_with(
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_LZMA)
