from django.shortcuts import render
import mimetypes
from django.http import StreamingHttpResponse, HttpResponse 

def download_file(request):
    fl_path = '/Users/km22/Documents/git_projects/monocle/mock-data/test.csv'
    filename = 'test.csv'
    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
