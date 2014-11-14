import json

from django.conf import settings
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from cellsliderdata.forms import CSAZipFileForm

from cellsliderdata.models import CSAZipFile


# @csrf_exempt
# def api_add_cell_slider_data(request):
#     if request.method != 'POST':
#         return HttpResponseNotAllowed(permitted_methods='POST')
#     api_key = request.POST.get('api_key')
#     if api_key != settings.CELL_SLIDER_DATA_API_KEY:
#         return HttpResponseForbidden()
#     json_data = request.POST.get('data', '')
#     try:
#         data = json.loads(json_data)
#     except ValueError:
#         return HttpResponseBadRequest()
#
#     return_data = {'processed': 0, 'rejected': {'count': 0, 'errors': {}}}
#     for d in data:
#         try:
#             Classification.FromData(d)
#             return_data['processed'] += 1
#         except Exception as ex:
#             return_data['rejected']['count'] += 1
#             d_id = d.get('id') if isinstance(d, dict) else None
#             if d_id:
#                 return_data['rejected']['errors'][d_id] = '%s (%s)' % (ex, type(ex))
#     return HttpResponse(json.dumps(return_data), content_type='application/json')
#

@login_required
def dashboard(request):
    return render(request, 'cellsliderdata/pages/dashboard.html')


@login_required
def classifications_import(request):
    form = CSAZipFileForm()
    if request.method == "POST":
        form = CSAZipFileForm(request.POST, request.FILES)
        if form.is_valid():
            csa_zip_file = CSAZipFile.Create(request.FILES['zip_file'])
    template_data = {'form': form}
    return render(request, 'cellsliderdata/pages/classifications_import.html', template_data)