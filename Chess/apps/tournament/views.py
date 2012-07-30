# Create your views here.
from django.shortcuts import render_to_response

from Chess.apps.tournament.models import *

def index(request):
    return render_to_response('tournament/index.html',{'info' : Tournament.get_all_info()})

def details(request, tournament_id):
    t = Tournament.objects.select_related().get(pk=tournament_id)
    t._tours.all()
