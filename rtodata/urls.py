from django.conf.urls import patterns, url
from rtodata.views import dashboard

urlpatterns = patterns(
    '',

    url(r'^$', dashboard, name='rto_data_dashboard'),
)
