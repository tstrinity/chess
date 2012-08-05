from django.shortcuts import render_to_response
from Chess.apps.tournament.models import Tournament
from django.contrib.auth.decorators import login_required

def index(request):
    return render_to_response('tournament/index.html',{'info' : Tournament.get_all_info()})

def details(request, tournament_id):
    info = Tournament.objects.get(pk=tournament_id).get_info_tour()
    return render_to_response('tournament/details.html', {'info' : info})

def ratings(request, tournament_id):
    info = Tournament.objects.get(pk = tournament_id).get_players_ratings()
    return render_to_response('tournament/ratings.html', {'info' : info})

@login_required()
def create_tournament(request):
    if request.method == 'post':
        pass
    return render_to_response('tournament/create.html', {})
