# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from Chess.apps.player.models import Player,PlayerAddForm

def index(request):
    ratings = Player.get_elo_ratings()
    paginator = Paginator(ratings, 12)
    page = request.GET.get('page')
    try:
        ratings = paginator.page(page)
    except PageNotAnInteger:
        ratings = paginator.page(1)
    except EmptyPage:
        ratings = paginator.page(paginator.num_pages)
    return render_to_response('player/index.html',
        {'info' : ratings},
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

