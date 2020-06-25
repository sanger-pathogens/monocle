from juno.api import views
import unittest
import io
from unittest.mock import patch


class TestDownload(unittest.TestCase):
    def setUp(self):
        self.laneId = "31663_7#113_1"

    def test_download_sample(self):
        with patch("juno.api.views.make_tarfile", return_value=io.BytesIO()) as tarMock:
            response = views.download_sample("request", self.laneId)
        self.assertEquals(
            response.get("Content-Disposition"),
            "attachment; filename=%s.tar.gz" % self.laneId,
        )
        tarMock.assert_called_once_with(self.laneId)

    def test_download_sample_file_not_found(self):
        with patch(
            "juno.api.views.make_tarfile", side_effect=FileNotFoundError
        ) as tarMock:
            try:
                views.download_sample("request", self.laneId)
            except:
                assert 404
        tarMock.assert_called_once_with(self.laneId)

