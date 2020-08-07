import io
import os
from django.http import FileResponse, StreamingHttpResponse, Http404
from django.conf import settings
from wsgiref.util import FileWrapper

from juno.api.downloads import make_tarfile


def download_read_1(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = "31663_7#113"

    filename = lane_id + "_1.fastq.gz"
    filepath = os.path.abspath(
        os.path.join(settings.DATA_DIR, lane_id, filename)
    )
    return FileResponse(
        open(filepath, "rb"), filename=filename, as_attachment=True
    )


def download_read_2(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = "31663_7#113"

    filename = lane_id + "_2.fastq.gz"
    filepath = os.path.abspath(
        os.path.join(settings.DATA_DIR, lane_id, filename)
    )
    return FileResponse(
        open(filepath, "rb"), filename=filename, as_attachment=True
    )


def download_assembly(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = "31663_7#113"

    filename = lane_id + ".fa"
    filepath = os.path.abspath(
        os.path.join(settings.DATA_DIR, lane_id, "spades_assembly/contigs.fa")
    )
    return FileResponse(
        open(filepath, "rb"), filename=filename, as_attachment=True
    )


def download_annotation(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = "31663_7#113"

    filename = lane_id + ".gff"
    filepath = os.path.abspath(
        os.path.join(
            settings.DATA_DIR,
            lane_id,
            "spades_assembly/annotation/" + lane_id + ".gff",
        )
    )
    return FileResponse(
        open(filepath, "rb"), filename=filename, as_attachment=True
    )


def download_sample(request, laneId):
    try:
        file_in_mem = make_tarfile(laneId)
    except FileNotFoundError:
        raise Http404
    filename = laneId + ".tar.gz"
    chunk_size = 8192
    response = StreamingHttpResponse(
        FileWrapper(io.BytesIO(file_in_mem.getvalue()), chunk_size),
        content_type=bytes,
    )
    response["Content-Length"] = file_in_mem.getbuffer().nbytes
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response
