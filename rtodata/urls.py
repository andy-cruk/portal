from django.conf.urls import patterns, url

from domain.views import classifications_import, classifications_import_processing_status, \
    classifications_import_processing, render_analysis_template, render_analysis_javascript
from rtodata.forms import RTOZipFileForm
from rtodata.models import RTODataRow
from rtodata.views import dashboard


urlpatterns = patterns(
    '',

    url(r'^import/processing/(?P<file_id>\d+)/status$',
        classifications_import_processing_status,
        {
            'processing_template': 'rtodata/components/classifications_import_process_progress.html',
            'error_template': 'rtodata/components/classifications_import_process_error.html'
        },
        name='rto_data_classifications_import_processing_status'),

    url(r'^import/processing/(?P<file_id>\d+)$',
        classifications_import_processing,
        {
            'template': 'rtodata/pages/classifications_import_processing.html',
            'data_row_class': RTODataRow
        },
        name='rto_data_classifications_import_processing'),

    url(r'^import$',
        classifications_import,
        {
            'zip_file_form': RTOZipFileForm,
            'success_redirect_url_name': 'rto_data_classifications_import_processing',
            'template': 'rtodata/pages/classifications_import.html'
        },
        name='rto_data_classifications_import'),



    url(r'^analysis/template$',
        render_analysis_template,
        name='rto_data_render_analysis_template'),

    url(r'^analysis/javascript$',
        render_analysis_javascript,
        name='rto_data_render_analysis_javascript'),

    url(r'^$', dashboard, name='rto_data_dashboard'),
)
