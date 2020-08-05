import os
from django.http import FileResponse
from django.conf import settings


def download_read_1(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = "31663_7#113"

    filename = lane_id + "_1.fastq.gz"
    filepath = os.path.abspath(
        os.path.join(settings.DATA_DIR, lane_id, filename)
    )
    return FileResponse(open(filepath, "rb"), filename=filename)


def download_read_2(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = "31663_7#113"

    filename = lane_id + "_2.fastq.gz"
    filepath = os.path.abspath(
        os.path.join(settings.DATA_DIR, lane_id, filename)
    )
    return FileResponse(open(filepath, "rb"), filename=filename)


def download_assembly(request, lane_id):
    if settings.USE_MOCK_LANE_DATA:
        lane_id = "31663_7#113"

    filename = lane_id + ".fa"
    filepath = os.path.abspath(
        os.path.join(settings.DATA_DIR, lane_id, "spades_assembly/contigs.fa")
    )
    return FileResponse(open(filepath, "rb"), filename=filename)


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
    return FileResponse(open(filepath, "rb"), filename=filename)
