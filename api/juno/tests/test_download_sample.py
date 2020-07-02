from juno.api import downloads
import unittest
from testfixtures import TempDirectory
import tarfile, io, os


class TestDownload(unittest.TestCase):
    def setUp(self):
        self.tempdir = TempDirectory()
        self.tempdir_path = self.tempdir.path
        downloads.DATA_DIR = self.tempdir_path

    def tearDown(self):
        self.tempdir.cleanup()
        pass

    def test_make_tarfile_returns_bytes_like_object(self):
        files = [
            "31663_7#113_1.fastq.gz",
            "31663_7#113_2.fastq.gz",
            "spades_assembly/contigs.fa",
            "spades_assembly/annotation/31663_7#113.gff",
        ]
        for file in files:
            self.tempdir.write(file, b"some data")
        tar_file = downloads.make_tarfile(self.tempdir_path)
        self.assertIsInstance(tar_file.getvalue(), bytes)
        file_in = io.BytesIO(tar_file.getvalue())
        tar = tarfile.open(mode="r:gz", fileobj=file_in)
        tar.extractall(self.tempdir_path + "/extract/")
        for file in files:
            os.path.isfile(self.tempdir_path + "/extract/" + file)

    def test_make_tarfile_returns_filenotfound(self):
        with self.assertRaises(FileNotFoundError):
            downloads.make_tarfile(self.tempdir_path)
