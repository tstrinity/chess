__author__ = 'tstrinity'

from django.conf.urls import url, patterns

urlpatterns = patterns('Chess.apps.tournament.views',
    url(r'^$', 'index'),
    url(r'^create/$', 'create'),
    url(r'^inactive/$', 'index_inactive'),
    url(r'^(?P<tournament_id>\d+)/$', 'details'),
    url(r'^(?P<tournament_id>\d+)/inactive/$', 'details_inactive'),
    url(r'^(?P<tournament_id>\d+)/rating/$', 'ratings'),
    url(r'^(?P<tournament_id>\d+)/start/$', 'start_tournament')
)