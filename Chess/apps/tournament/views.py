# Create your views here.
from django.shortcuts import render_to_response

from Chess.apps.tournament.models import *

def index(request):
    return render_to_response('tournament/index.html',{})