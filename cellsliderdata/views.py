import json
import os
import tarfile
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from cellsliderdata.analyzers import BaseAnalyzer
from cellsliderdata.decorators import async

from cellsliderdata.forms import CSAZipFileForm
from cellsliderdata.models import CSAZipFile, CSAZipFileProcess, CSADataFile


@login_required
def dashboard(request):
    active_data_file = CSADataFile.objects.all().order_by('-updated').first()
    template_data = {
        'current_data_uploaded': active_data_file.updated,
        'analyzers': settings.CELL_SLIDER_ANALYSIS,
    }
    return render(request, 'cellsliderdata/pages/dashboard.html', template_data)


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
def classifications_import(request):
    form = CSAZipFileForm()
    if request.method == "POST" and request.is_ajax():
        form = CSAZipFileForm(request.POST, request.FILES)
        if form.is_valid():
            csa_zip_file = CSAZipFile.Create(request.FILES['zip_file'])
            return HttpResponse(reverse(classifications_import_processing, kwargs={'file_id': csa_zip_file.id}))
        else:
            return HttpResponseBadRequest([''.join(["<p>%s</p>" % _e for _e in e]) for e in form.errors.values()])
    template_data = {'form': form}
    return render(request, 'cellsliderdata/pages/classifications_import.html', template_data)


@login_required
@async
def classifications_import_processing(request, file_id):
    csa_zip_file = get_object_or_404(CSAZipFile, id=file_id)
    template_data = {'csa_zip_file': csa_zip_file}
    yield render(request, 'cellsliderdata/pages/classifications_import_processing.html', template_data)
    CSAZipFileProcess.RunProcessForZipFile(csa_zip_file)


@login_required
def classifications_import_processing_status(request, file_id):
    csa_zip_file = get_object_or_404(CSAZipFile, id=file_id)
    csa_zip_file_process = get_object_or_404(CSAZipFileProcess, csa_zip_file=csa_zip_file)
    state = 'processing'
    template = None
    if csa_zip_file_process.state == CSAZipFileProcess.STATE_START:
        template = render_to_string('cellsliderdata/components/classifications_import_process_progress.html', {
            'progress': 10,
            'steps_done': ['Uploaded file'],
            'steps_doing': ['Unzipping uploaded file'],
            'steps_todo': ['Loading CSV file', 'Validate file format', 'Import file data']})
    elif csa_zip_file_process.state == CSAZipFileProcess.STATE_UNZIPPED:
        template = render_to_string('cellsliderdata/components/classifications_import_process_progress.html', {
            'progress': 30,
            'steps_done': ['Uploaded file', 'Unzipped uploaded file'],
            'steps_doing': ['Loading CSV file'],
            'steps_todo': ['Validating file format', 'Import file data']})
    elif csa_zip_file_process.state == CSAZipFileProcess.STATE_CSV_FILE_EXISTS:
        template = render_to_string('cellsliderdata/components/classifications_import_process_progress.html', {
            'progress': 40,
            'steps_done': ['Uploaded file', 'Unzipped uploaded file', 'Loading CSV file'],
            'steps_doing': ['Validating file format'],
            'steps_todo': ['Import file data']})
    elif csa_zip_file_process.state == CSAZipFileProcess.STATE_IMPORTING:
        template = render_to_string('cellsliderdata/components/classifications_import_process_progress.html', {
            'progress': csa_zip_file_process.data_import_progress,
            'steps_done': ['Uploaded file', 'Unzipped uploaded file', 'Loading CSV file', 'Validating file format'],
            'steps_doing': ['Import file data'],
            'steps_todo': []})
    elif csa_zip_file_process.state == CSAZipFileProcess.STATE_FINISHED:
        state = 'finished'
        template = render_to_string('cellsliderdata/components/classifications_import_process_progress.html', {
            'progress': 100,
            'steps_done': [
                'Uploaded file', 'Unzipped uploaded file', 'Loading CSV file', 'Validating file format',
                'Import file data'],
            'steps_doing': [],
            'steps_todo': []})
    elif csa_zip_file_process.state == CSAZipFileProcess.STATE_ERROR:
        state = 'error'
        template = render_to_string('cellsliderdata/components/classifications_import_process_error.html', {
            'csa_zip_file_process': csa_zip_file_process})
    return HttpResponse(json.dumps({'status': state, 'template': template}), content_type='application/json')

