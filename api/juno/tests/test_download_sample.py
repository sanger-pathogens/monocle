import io
import os
import tarfile
import unittest

# from django.test import override_settings
from django.conf import settings
from testfixtures import TempDirectory

from juno.api import downloads


class TestMakeTarfile(unittest.TestCase):
    def setUp(self):
        # create DATA_DIR
        self.data_dir = TempDirectory()

        # create single lane directory
        self.lane_id = "31663_7#113"
        # self.lane_dir = self.data_dir.makedir(self.lane_id)

        # create mock files for single lane
        self.files = [
            self.lane_id + "_1.fastq.gz",
            self.lane_id + "_2.fastq.gz",
            "spades_assembly/contigs.fa",
            "spades_assembly/annotation/" + self.lane_id + ".gff",
        ]
        for filename in self.files:
            self.data_dir.write(
                "/".join([self.lane_id, filename]), b"some data"
            )

        # override settings
        settings.DATA_DIR = self.data_dir.path
        settings.USE_MOCK_LANE_DATA = False

    def tearDown(self):
        self.data_dir.cleanup()

    def test_returns_bytes_for_valid_lane(self):
        tar_file = downloads.make_tarfile(self.lane_id)

        # file?
        self.assertIsInstance(tar_file.getvalue(), bytes)

        # tarfile?
        file_in = io.BytesIO(tar_file.getvalue())
        tar = tarfile.open(mode="r:gz", fileobj=file_in)
        tar.extractall(self.lane_id + "/extract/")

        # contains individual data files?
        for file in self.files:
            os.path.isfile(self.lane_id + "/extract/" + file)

    def test_raises_filenotfound_for_invalid_lane(self):
        with self.assertRaises(FileNotFoundError):
            downloads.make_tarfile("invalid_lane_id")
