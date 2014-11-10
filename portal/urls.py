from django.conf.urls import patterns, url
from portal.views import hello_world, portal_home, portal_login

urlpatterns = patterns(
    '',
    url(r'^hello', hello_world, name='hello_world'),

    # rules that do not require user authntication
    url(r'^login$', portal_login, name='portal_login'),

    # Rule to catch empty urls
    url(r'', portal_home, name='portal_home'),
)
