from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',),
    url(r'^tours/', include('Chess.apps.tour.urls')),
    url(r'^tournaments/', include('Chess.apps.tournament.urls')),
    url(r'^games/', include('Chess.apps.game.urls')),
    url(r'^players/', include('Chess.apps.player.urls')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
)
