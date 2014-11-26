import json
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from cellsliderdata.decorators import async
from cellsliderdata.forms import CSAZipFileForm
from cellsliderdata.models import CellSliderDataRow
from domain.analyzers import BaseAnalyzer
from domain.models import CSAZipFile, CSAZipFileProcess

__author__ = 'matt'


@login_required
def classifications_import_processing_status(request, file_id, processing_template, error_template):
    csa_zip_file = get_object_or_404(CSAZipFile, id=file_id)
    csa_zip_file_process = get_object_or_404(CSAZipFileProcess, csa_zip_file=csa_zip_file)
    state, template_data = csa_zip_file_process.get_csa_zip_file_process()
    if state == 'processing':
        template = render_to_string(
            processing_template,
            template_data)
    else:
        template = render_to_string(
            error_template,
            template_data)
    return HttpResponse(json.dumps({'status': state, 'template': template}), content_type='application/json')


@login_required
@async
def classifications_import_processing(request, file_id, template):
    csa_zip_file = get_object_or_404(CSAZipFile, id=file_id)
    template_data = {'csa_zip_file': csa_zip_file}
    yield render(request, template, template_data)
    CSAZipFileProcess.RunProcessForZipFile(csa_zip_file, CellSliderDataRow)


@login_required
def classifications_import(request, zip_file_form, success_redirect_url_name, template):
    form = zip_file_form()
    if request.method == "POST" and request.is_ajax():
        form = zip_file_form(request.POST, request.FILES)
        if form.is_valid():
            csa_zip_file = CSAZipFile.Create(request.FILES['zip_file'])
            return HttpResponse(
                reverse(success_redirect_url_name, kwargs={'file_id': csa_zip_file.id}))
        else:
            return HttpResponseBadRequest([''.join(["<p>%s</p>" % _e for _e in e]) for e in form.errors.values()])
    template_data = {'form': form}
    return render(request, template, template_data)


@login_required
def render_analysis_javascript(request):
    analyzer_name = request.GET.get('analyzer')
    if not analyzer_name:
        return HttpResponse('')
    cache_key = "%s_javascript" % analyzer_name
    javascript = cache.get(cache_key, None)
    if not javascript:
        javascript = ''
        if analyzer_name:
            analyzer = BaseAnalyzer.GetAnalyzerByName(analyzer_name, request)
            if analyzer:
                javascript = analyzer.get_javascript()
        cache.set(cache_key, javascript, None)
    return HttpResponse(javascript, content_type="application/x-javascript")


@login_required
def render_analysis_template(request):
    analyzer_name = request.GET.get('analyzer')
    if not analyzer_name:
        return HttpResponse('')
    cache_key = "%s_template" % analyzer_name
    template = cache.get(cache_key, None)
    if not template:
        template = '' \
                   '<div class="alert alert-warning media>' \
                   '    <i class="fa fa-warning fa-4x pull-left media-object"></i>' \
                   '    <div class="media-body">' \
                   '        <h4 class="media-heading">This analyser failed to load</h4>' \
                   '        <p></p>' \
                   '    </div>' \
                   '</div>'
        if analyzer_name:
            analyzer = BaseAnalyzer.GetAnalyzerByName(analyzer_name, request)
            if analyzer:
                template = analyzer.get_template()
        cache.set(cache_key, template, None)
    return HttpResponse(
        json.dumps({'template': template, 'name': request.GET.get('name'), 'analyzer_name': analyzer_name}),
        content_type='application/json')