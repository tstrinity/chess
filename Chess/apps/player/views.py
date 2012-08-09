# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from Chess.apps.player.models import Player,PlayerAddForm

def index(request):
    return render_to_response('player/index.html',
        {'info' : Player.get_elo_ratings()},
        context_instance=RequestContext(request)
    )

@login_required()
def create(request):
    form = PlayerAddForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=True)
            return redirect('Chess.apps.player.views.index')
    return render_to_response('player/create.html', {'form': form},
        context_instance=RequestContext(request)
    )

