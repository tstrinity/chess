# Create your views here.

from django.shortcuts import get_object_or_404, render_to_response
from Chess.apps.game.models import Game
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect


def setWinner(request, game_id):
    if request.method == 'POST':
        c = {}
        c.update(csrf(request))
        game = get_object_or_404(Game, pk=game_id)
        result = request.POST['winner']
        if game.set_match_result(result) == False:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponseRedirect(game.tour.tournament.return_url())