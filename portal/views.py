from django.http import HttpResponse

__author__ = 'paters01'

def hello_world(request):
    return HttpResponse("Hello World!")