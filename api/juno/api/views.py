from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse 
from wsgiref.util import FileWrapper
import os 
import mimetypes
from django.conf import settings


def download_file(request, laneId):
    the_file = os.path.abspath(
        os.path.join(
            os.path.join(getattr(settings, "BASE_DIR", None),os.pardir
            ),
            "mock-data/" + "31663_7#113" + ".tar.gz",
        )
    )
    filename = os.path.basename(the_file)
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(the_file, 'rb'), chunk_size), 
                                     content_type=mimetypes.guess_type(the_file)[0])
    response['Content-Length'] = os.path.getsize(the_file)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
