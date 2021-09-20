from unittest      import TestCase
from unittest.mock import create_autospec
from pathlib       import Path
from zipfile       import ZipFile, ZIP_LZMA

from file import zip_files, WRITE_MODE

FILES = ['a_file.txt', 'another_file.fastq']
BASENAME = 'batches'
ZIP_FILE_NAME = BASENAME + '.zip'

class TestFileUtil(TestCase):

  ZipFileMock = create_autospec(ZipFile)

  def tearDown(self):
    self.ZipFileMock.reset_mock()

  def test_zip_files(self):
    zipfile_instance = self.ZipFileMock.return_value
    # Make the instance of `ZipFileMock` available in the context manager of the tested `zip_files()`.
    zipfile_instance.__enter__.return_value = zipfile_instance
    location = 'downloads'

    zip_files(FILES,
      basename=BASENAME,
      location=location,
      ZipFileInjected=self.ZipFileMock)

    expected_zip_file_full_name = Path(location) / ZIP_FILE_NAME
    self.ZipFileMock.assert_called_once_with(
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_LZMA)
    self.assertEqual(zipfile_instance.write.call_count, len(FILES))
    for file in FILES:
      zipfile_instance.write.assert_any_call(file)

  def test_zip_files_to_current_folder_if_no_location_given(self):
    zip_files(FILES, basename=BASENAME, ZipFileInjected=self.ZipFileMock)

    expected_zip_file_full_name = Path('.') / ZIP_FILE_NAME
    self.ZipFileMock.assert_called_once_with(
      expected_zip_file_full_name, mode=WRITE_MODE, compression=ZIP_LZMA)

  def test_does_not_zip_if_no_files_passed(self):
    zip_files([], basename=BASENAME, ZipFileInjected=self.ZipFileMock)

    self.ZipFileMock.assert_not_called()
