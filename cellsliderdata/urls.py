from django.conf.urls import patterns, url
from cellsliderdata.views import dashboard, classifications_import

urlpatterns = patterns(
    '',

    # Html views
    url(r'^import$', classifications_import, name='cell_slider_data_classifications_import'),

    url(r'^$', dashboard, name='cell_slider_data_dashboard'),
)
