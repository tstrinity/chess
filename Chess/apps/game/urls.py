__author__ = 'tstrinity'

from django.conf.urls import url, patterns

urlpatterns = patterns('Chess.apps.game.views',
    url(r'setWinner/(?P<game_id>\d+)/$', 'setWinner'),
)