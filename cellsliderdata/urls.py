from django.conf.urls import patterns, url
from cellsliderdata.views import dashboard, classifications_import, classifications_import_processing
from cellsliderdata.views import classifications_import_processing_status, render_analysis_template
from cellsliderdata.views import render_analysis_javascript

urlpatterns = patterns(
    '',

    # Html views
    url(r'^import/processing/(?P<file_id>\d+)/status$',
        classifications_import_processing_status,
        name='cell_slider_data_classifications_import_processing_status'),

    url(r'^import/processing/(?P<file_id>\d+)$',
        classifications_import_processing,
        name='cell_slider_data_classifications_import_processing'),

    url(r'^import$',
        classifications_import,
        name='cell_slider_data_classifications_import'),

    url(r'^analysis/template$',
        render_analysis_template,
        name='cell_slider_data_render_analysis_template'),

    url(r'^analysis/javascript$',
        render_analysis_javascript,
        name='cell_slider_data_render_analysis_javascript'),

    url(r'^$', dashboard, name='cell_slider_data_dashboard'),
)
