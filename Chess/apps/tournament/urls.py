__author__ = 'tstrinity'

from django.conf.urls import url, patterns

urlpatterns = patterns('Chess.apps.tournament.views',
    url(r'^$', 'index'),
    url(r'(?P<tournament_id>\d+)/$', 'details'),
)