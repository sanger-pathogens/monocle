from juno.api import downloads
import unittest
from testfixtures import TempDirectory
import tarfile, io, os


class TestDownload(unittest.TestCase):
    def setUp(self):
        self.tempdir = TempDirectory()
        self.tempdir_path = self.tempdir.path

    def tearDown(self):
        self.tempdir.cleanup()
        pass

    def test_make_tarfile_returns_bytes_like_object(self):
        self.tempdir.write("31663_7#113_1.fastq.gz", b"pair 1")
        self.tempdir.write("31663_7#113_2.fastq.gz", b"pair 2")
        self.tempdir.write("spades_assembly/contigs.fa", b"assembly")
        self.tempdir.write("spades_assembly/annotation/31663_7#113.gff", b"annotation")
        tar_file = downloads.make_tarfile(self.tempdir_path)
        self.assertIsInstance(tar_file, bytes)
        file_in = io.BytesIO(tar_file)
        tar = tarfile.open(mode="r:gz", fileobj=file_in)
        tar.extractall("~/Downloads")

    def test_make_tarfile_returns_filenotfound(self):
        with self.assertRaises(FileNotFoundError):
            downloads.make_tarfile(self.tempdir_path)
