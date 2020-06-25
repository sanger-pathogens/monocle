from django.http import StreamingHttpResponse, Http404
from wsgiref.util import FileWrapper
import io
from juno.api.downloads import make_tarfile


def download_sample(request, laneId):
    try:
        file_in_mem = make_tarfile(laneId)
    except FileNotFoundError:
        raise Http404
    filename = laneId + ".tar.gz"
    chunk_size = 8192
    response = StreamingHttpResponse(
        FileWrapper(io.BytesIO(file_in_mem.getvalue()), chunk_size), content_type=bytes,
    )
    response["Content-Length"] = file_in_mem.getbuffer().nbytes
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response
