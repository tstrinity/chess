__author__ = 'tstrinity'

from django.conf.urls import url, patterns

urlpatterns = patterns('Chess.apps.tour.views',
    url(r'(?P<tour_id>\d+)/$', 'details'),
)