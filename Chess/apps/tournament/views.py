# Create your views here.

from django.shortcuts import render_to_response
from Chess.apps.tournament.models import Tournament

def index(request):
    return render_to_response('tournament/index.html',{'info' : Tournament.get_all_info()})

def details(request, tournament_id):
    info = Tournament.objects.get(pk=tournament_id).get_info_tour()
    return render_to_response('tournament/details.html', {'info' : info})

def ratings(request, tournament_id):
    info = Tournament.objects.get(pk = tournament_id).get_players_ratings()
    return render_to_response('tournament/ratings.html', {'info' : info})