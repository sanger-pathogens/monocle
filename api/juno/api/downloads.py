import tarfile, io, os
from django.http import StreamingHttpResponse, HttpResponse, Http404
from wsgiref.util import FileWrapper
import mimetypes
import time


def make_tarfile(source_dir):
    filenames = {
        "31663_7#113_1.fastq.gz": "31663_7#113_1.fastq.gz",
        "31663_7#113_2.fastq.gz": "31663_7#113_2.fastq.gz",
        "spades_assembly/contigs.fa": "spades_contigs.fa",
        "spades_assembly/annotation/31663_7#113.gff": "spades_annotation.gff",
    }
    out_file = io.BytesIO()
    with tarfile.open(fileobj=out_file, mode="w:gz") as tar:
        for file in filenames:
            file_path = source_dir + "/" + file
            tar.add(file_path, arcname=filenames[file])
    return out_file.getvalue()


def stream_sample(archived_file, file_path):
    filename = os.path.basename(file_path)
    chunk_size = 8192
    archived_file = io.BytesIO(archived_file)
    response = StreamingHttpResponse(
        FileWrapper(archived_file, chunk_size), content_type=bytes,
    )
    # response["Content-Length"] = os.path.getsize(archived_file.getvalue())
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response
