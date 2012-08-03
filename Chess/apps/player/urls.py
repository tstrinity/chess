__author__ = 'tstrinity'

from django.conf.urls import url, patterns

urlpatterns = patterns('Chess.apps.player.views',
    url(r'rating/$', 'index'),
)