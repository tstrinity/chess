# Create your views here.

from django.shortcuts import render_to_response
from Chess.apps.player.models import Player

def index(request):
    return render_to_response('player/index.html', {'info' : Player.get_elo_ratings()})