from django.conf.urls import patterns, url
from django.contrib.auth.views import logout
from cellsliderdata.views import api_add_cell_slider_data, classifications_list
from portal.views import hello_world, portal_home, portal_login

urlpatterns = patterns(
    '',

    # API urls
    url('^api/add-json-data', api_add_cell_slider_data, name='cell_slider_data_api_add_data'),

    # Html views
    url('^list', classifications_list, name='cell_slider_data_classifications_list')
)
