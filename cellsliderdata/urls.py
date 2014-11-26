from django.conf.urls import patterns, url
from cellsliderdata.forms import CSAZipFileForm
from cellsliderdata.models import CellSliderDataRow
from cellsliderdata.views import dashboard
from domain.views import classifications_import_processing_status, classifications_import_processing, \
    classifications_import, render_analysis_javascript, render_analysis_template

urlpatterns = patterns(
    '',

    # Html views
    url(r'^import/processing/(?P<file_id>\d+)/status$',
        classifications_import_processing_status,
        {
            'processing_template': 'cellsliderdata/components/classifications_import_process_progress.html',
            'error_template': 'cellsliderdata/components/classifications_import_process_error.html'
        },
        name='cell_slider_data_classifications_import_processing_status'),

    url(r'^import/processing/(?P<file_id>\d+)$',
        classifications_import_processing,
        {
            'template': 'cellsliderdata/pages/classifications_import_processing.html',
            'data_row_class': CellSliderDataRow
        },
        name='cell_slider_data_classifications_import_processing'),

    url(r'^import$',
        classifications_import,
        {
            'zip_file_form': CSAZipFileForm,
            'success_redirect_url_name': 'cell_slider_data_classifications_import_processing',
            'template': 'cellsliderdata/pages/classifications_import.html'
        },
        name='cell_slider_data_classifications_import'),

    url(r'^analysis/template$',
        render_analysis_template,
        name='cell_slider_data_render_analysis_template'),

    url(r'^analysis/javascript$',
        render_analysis_javascript,
        name='cell_slider_data_render_analysis_javascript'),

    url(r'^$', dashboard, name='cell_slider_data_dashboard'),
)
