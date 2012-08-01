from django.conf.urls import patterns, include, url
from django.contrib import admin
import Chess

admin.autodiscover()

urlpatterns = patterns('django.views.generic.simple',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tours/', include('Chess.apps.tour.urls')),
    url(r'^tournaments/', include('Chess.apps.tournament.urls')),
)
