from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
from wsgiref.util import FileWrapper
import os
import mimetypes
import tarfile
from django.conf import settings


def download_file(request, laneId):
    lane_dir = os.path.abspath(
        os.path.join(
            os.path.join(getattr(settings, "BASE_DIR", None), os.pardir),
            "mock-data/" + "31663_7#113",
        )
    )
    archive_file = lane_dir + "tar.gz"
    make_tarfile(archive_file, lane_dir)
    response = stream_file(archive_file)
    return response


def filter_file(thing):
    print("{thing.name}".format(thing=thing))
    if thing.name in [
        "31663_7#113",
        "31663_7#113/31663_7#113_1.fastq.gz",
        "31663_7#113/31663_7#113_2.fastq.gz",
        "31663_7#113/spades_assembly",
        "31663_7#113/spades_assembly/contigs.fa",
        "31663_7#113/spades_assembly/annotation",
        "31663_7#113/spades_assembly/annotation/31663_7#113.gff",
    ]:
        return thing


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(
            source_dir,
            arcname=os.path.basename(source_dir),
            recursive=True,
            filter=filter_file,
        )


def stream_file(file_path):
    filename = os.path.basename(file_path)
    chunk_size = 8192
    response = StreamingHttpResponse(
        FileWrapper(open(file_path, "rb"), chunk_size),
        content_type=mimetypes.guess_type(file_path)[0],
    )
    response["Content-Length"] = os.path.getsize(file_path)
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response
