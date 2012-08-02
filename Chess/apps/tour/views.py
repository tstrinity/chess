# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from Chess.apps.tournament.models import Tour

def details(request, tour_id):
    info = Tour.objects.get(pk = tour_id).get_games_info()
    csrfContext = RequestContext(request)
    return render_to_response('tour/details.html', {'info' : info}, context_instance = csrfContext)


