from django.shortcuts import render
import mimetypes
from django.http import StreamingHttpResponse, HttpResponse 
import os 
from wsgiref.util import FileWrapper
 

def download_file(request):
    the_file = '/Users/km22/Documents/git_projects/monocle/mock-data/test.csv'
    filename = os.path.basename(the_file)
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(the_file, 'rb'), chunk_size), 
                                     content_type=mimetypes.guess_type(the_file)[0])
    response['Content-Lenght'] = os.path.getsize(the_file)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
