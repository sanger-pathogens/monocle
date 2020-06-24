from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse, Http404
from wsgiref.util import FileWrapper
import tarfile
import os
from django.conf import settings
from juno.api.downloads import make_tarfile, stream_sample

# TODO: replace fixed mock file with actual file for lane
DATA_DIR = os.path.join(
    os.path.join(getattr(settings, "BASE_DIR", None), os.pardir),
    "mock-data/" + "31663_7#113",
)


def download_sample(request, laneId):
    lane_dir = os.path.abspath(DATA_DIR)
    try:
        file_in_mem = make_tarfile(lane_dir)
    except FileNotFoundError:
        raise Http404
    filename = lane_dir + ".tar.gz"
    response = stream_sample(file_in_mem, filename)
    return response
