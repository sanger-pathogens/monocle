import io
import os
import tarfile
import unittest
from django.conf import settings
from testfixtures import TempDirectory

from juno.api import downloads


class TestMakeTarfileReal(unittest.TestCase):
    def setUp(self):
        # create DATA_DIR
        self.data_dir = TempDirectory()
        self.data_dir.makedir("reads")
        self.data_dir.makedir("assembly")
        self.data_dir.makedir("annotation")

        # create extraction directory
        self.extract_dir = TempDirectory()

        # test lane
        self.lane_id = "31663_7#113"

        # create mock files for single lane
        self.files = [
            os.path.join("reads", self.lane_id + "_1.fastq.gz"),
            os.path.join("reads", self.lane_id + "_2.fastq.gz"),
            os.path.join("assembly", self.lane_id + ".contigs_spades.fa"),
            os.path.join("annotation", self.lane_id + ".spades.gff")
        ]

        # define what we expect to find in a tar download
        self.expected_archive_files = [
            self.lane_id + "_1.fastq.gz",
            self.lane_id + "_2.fastq.gz",
            self.lane_id + ".contigs_spades.fa",
            self.lane_id + ".spades.gff"
        ]

        for file in self.files:
            self.data_dir.write(file, b"some data")

        # override settings
        settings.DATA_DIR = self.data_dir.path
        settings.USE_MOCK_LANE_DATA = False

    def tearDown(self):
        self.data_dir.cleanup()
        self.extract_dir.cleanup()

    def test_returns_bytes_for_valid_lane(self):
        tar_file = downloads.make_tarfile(self.lane_id)

        # file?
        self.assertIsInstance(tar_file.getvalue(), bytes)

        # tarfile?
        file_in = io.BytesIO(tar_file.getvalue())
        tar = tarfile.open(mode="r:gz", fileobj=file_in)

        tar.extractall(self.extract_dir.path + "/extract/")

        # contains individual data files?
        for filename in self.expected_archive_files:
            os.path.isfile(self.extract_dir.path + "/extract/" + filename)

    def test_raises_filenotfound_for_invalid_lane(self):
        with self.assertRaises(FileNotFoundError):
            downloads.make_tarfile("invalid_lane_id")


class TestMakeTarfileMock(unittest.TestCase):
    def setUp(self):
        # create extraction directory
        self.extract_dir = TempDirectory()

        # create single lane directory
        self.lane_id = "31663_7#113"
        self.other_lane_id = "31663_7#115"

        # define what we expect to find in a download
        self.expected_archive_files = [
            self.lane_id + "_1.fastq.gz",
            self.lane_id + "_2.fastq.gz",
            self.lane_id + ".contigs_spades.fa",
            self.lane_id + ".spades.gff"
        ]

    def tearDown(self):
        self.extract_dir.cleanup()

    def get_file_count(self, dir):
        return len(
            [
                name
                for name in os.listdir(dir)
                if os.path.isfile(os.path.join(dir, name))
            ]
        )

    def test_returns_bytes_for_actual_lane(self):
        tar_file = downloads.make_tarfile(self.lane_id)

        # file?
        self.assertIsInstance(tar_file.getvalue(), bytes)

        # tarfile?
        file_in = io.BytesIO(tar_file.getvalue())
        tar = tarfile.open(mode="r:gz", fileobj=file_in)

        tar.extractall(self.extract_dir.path + "/extract/")

        # contains individual data files?
        for filename in self.expected_archive_files:
            os.path.isfile(self.extract_dir.path + "/extract/" + filename)

    def test_returns_bytes_for_other_lane(self):
        """
            Although we specify a different lane here, because we are operating
            in mock mode it will just use the default mock lane
        """

        tar_file = downloads.make_tarfile(self.other_lane_id)

        # file?
        self.assertIsInstance(tar_file.getvalue(), bytes)

        # tarfile?
        file_in = io.BytesIO(tar_file.getvalue())
        tar = tarfile.open(mode="r:gz", fileobj=file_in)

        tar.extractall(self.extract_dir.path + "/extract/")

        # contains individual data files?
        for filename in self.expected_archive_files:
            os.path.isfile(self.extract_dir.path + "/extract/" + filename)
