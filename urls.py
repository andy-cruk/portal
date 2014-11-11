from django.conf.urls import patterns, include, url
from django.contrib import admin
from portal.views import hello_world

urlpatterns = patterns(
    '',
    # Urls for the admin site
    url(r'^admin/', include(admin.site.urls)),

    # Include app specific url includes here
    url(r'^cellsliderdata/', include('cellsliderdata.urls')),

    # Urls for the main portal functions matches anything not caught by any other handler
    url(r'', include("portal.urls"))
)
