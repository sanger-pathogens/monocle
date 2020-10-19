import io
from django.http import FileResponse, StreamingHttpResponse, Http404
from django.conf import settings
from wsgiref.util import FileWrapper

from juno.api import downloads

MOCK_LANE_ID = "31663_7#113"


def download_read_1(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = MOCK_LANE_ID

    filename = downloads.get_read1_fastq_download_name(lane_id)
    filepath = downloads.get_read1_fastq_file_path(lane_id)

    return FileResponse(
        open(filepath, "rb"), filename=filename, as_attachment=True
    )


def download_read_2(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = MOCK_LANE_ID

    filename = downloads.get_read2_fastq_download_name(lane_id)
    filepath = downloads.get_read2_fastq_file_path(lane_id)

    return FileResponse(
        open(filepath, "rb"), filename=filename, as_attachment=True
    )


def download_assembly(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = MOCK_LANE_ID

    filename = downloads.get_spades_assembly_contigs_download_name(lane_id)
    filepath = downloads.get_spades_assembly_contigs_file_path(lane_id)

    return FileResponse(
        open(filepath, "rb"), filename=filename, as_attachment=True
    )


def download_annotation(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = MOCK_LANE_ID

    filename = downloads.get_spades_annotation_gff_download_name(lane_id)
    filepath = downloads.get_spades_annotation_gff_file_path(lane_id)

    return FileResponse(
        open(filepath, "rb"), filename=filename, as_attachment=True
    )


def download_sample(request, laneId):
    try:
        file_in_mem = downloads.make_tarfile(laneId)
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
