import json
from django.conf import settings
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from cellsliderdata.models import Classification

@csrf_exempt
def api_add_cell_slider_data(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods='POST')
    api_key = request.POST.get('api_key')
    if api_key != settings.CELL_SLIDER_DATA_API_KEY:
        return HttpResponseForbidden()
    json_data = request.POST.get('data', '')
    try:
        data = json.loads(json_data)
    except ValueError:
        return HttpResponseBadRequest()

    return_data = {'processed': 0, 'rejected': {'count': 0, 'errors': {}}}
    for d in data:
        try:
            Classification.FromData(d)
            return_data['processed'] += 1
        except Exception as ex:
            return_data['rejected']['count'] += 1
            d_id = d.get('id') if isinstance(d, dict) else None
            if d_id:
                return_data['rejected']['errors'][d_id] = '%s (%s)' % (ex, type(ex))
    return HttpResponse(json.dumps(return_data), content_type='application/json')

@login_required
def classifications_list(request):
    all_classifications = Classification.objects.all()
    paginator = Paginator(all_classifications, 25)

    page = request.GET.get('page')
    try:
        classifications = paginator.page(page)
    except PageNotAnInteger:
        classifications = paginator.page(1)
    except EmptyPage:
        classifications = paginator.page(paginator.num_pages)

    template_data = {"classifications": classifications}
    return render(request, 'cellsliderdata/pages/classifications_list.html', template_data)