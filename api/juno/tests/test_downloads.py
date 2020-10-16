import gzip
from django.test import TestCase
from django.conf import settings
from django.utils.encoding import force_bytes


def response_content(response):
    parts = [force_bytes(s) for s in response.streaming_content]
    return b"".join(parts)


class TestDownloads(TestCase):
    def setUp(self):
        # example lane
        self.lane_id = "31663_7#113"
        self.url_read1 = "/read1/31663_7%23113"
        self.url_read2 = "/read2/31663_7%23113"
        self.url_assembly = "/assembly/31663_7%23113"
        self.url_annotation = "/annotation/31663_7%23113"
        self.filename_read1 = "31663_7#113_1.fastq.gz"
        self.filename_read2 = "31663_7#113_2.fastq.gz"
        self.filename_assembly = "31663_7#113.contigs_spades.fa"
        self.filename_annotation = "31663_7#113.spades.gff"

        # small mock data files
        settings.USE_MOCK_LANE_DATA = True
        settings.DATA_DIR = settings.MOCK_DATA_DIR

    def test_read1(self):
        response = self.client.get(self.url_read1)

        # success?
        self.assertEqual(response.status_code, 200)

        # attachment?
        self.assertEquals(
            response.get("Content-Disposition"),
            'attachment; filename="{}"'.format(self.filename_read1),
        )

        # non-empty file?
        content_length = int(response.get("Content-Length"))
        content = response_content(response)
        self.assertGreater(content_length, 0)
        self.assertEquals(content_length, len(content))

        # file content?
        decompressed_content = gzip.decompress(content)
        self.assertEqual(decompressed_content, b"file1\n")

    def test_read2(self):
        response = self.client.get(self.url_read2)

        # success?
        self.assertEqual(response.status_code, 200)

        # attachment?
        self.assertEquals(
            response.get("Content-Disposition"),
            'attachment; filename="{}"'.format(self.filename_read2),
        )

        # non-empty file?
        content_length = int(response.get("Content-Length"))
        content = response_content(response)
        self.assertGreater(content_length, 0)
        self.assertEquals(content_length, len(content))

        # file content?
        decompressed_content = gzip.decompress(content)
        self.assertEqual(decompressed_content, b"file2\n")

    def test_assembly(self):
        response = self.client.get(self.url_assembly)

        # success?
        self.assertEqual(response.status_code, 200)

        # attachment?
        self.assertEquals(
            response.get("Content-Disposition"),
            'attachment; filename="{}"'.format(self.filename_assembly),
        )

        # non-empty file?
        content_length = int(response.get("Content-Length"))
        content = response_content(response)
        self.assertGreater(content_length, 0)
        self.assertEquals(content_length, len(content))

        # file content?
        self.assertEqual(content, b"assembly\n")

    def test_annotation(self):
        response = self.client.get(self.url_annotation)

        # success?
        self.assertEqual(response.status_code, 200)

        # attachment?
        self.assertEquals(
            response.get("Content-Disposition"),
            'attachment; filename="{}"'.format(self.filename_annotation),
        )

        # non-empty file?
        content_length = int(response.get("Content-Length"))
        content = response_content(response)
        self.assertGreater(content_length, 0)
        self.assertEquals(content_length, len(content))

        # file content?
        self.assertEqual(content, b"annotation\n")
