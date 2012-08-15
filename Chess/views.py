from django.template.context import RequestContext

__author__ = 'ts.trinity'
from Chess.apps.tournament.models import Tournament

from django.shortcuts import get_list_or_404, render_to_response

def index(request):
    tournaments = Tournament.get_all_info(True)
    return render_to_response('index.html', {'tournaments' : tournaments}, context_instance=RequestContext(request))