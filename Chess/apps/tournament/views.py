from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext
from Chess.apps.tournament.models import Tournament, TournamentAddForm
from django.contrib.auth.decorators import login_required

def index(request):
    return render_to_response('tournament/index.html',
        {'info' : Tournament.get_all_info(started=True)},
        context_instance=RequestContext(request)
    )

def details(request, tournament_id):
    t = get_object_or_404(Tournament, pk = tournament_id, active=True)
    info = t.get_info_tour()
    return render_to_response('tournament/details.html',
        {'info' : info},
        context_instance=RequestContext(request)
    )

def ratings(request, tournament_id):
    info = get_object_or_404(Tournament, pk = tournament_id).get_players_ratings()
    return render_to_response('tournament/ratings.html',
        {'info' : info}
        , context_instance=RequestContext(request)
    )

@login_required()
def create(request):
    form = TournamentAddForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('Chess.apps.tournament.views.index_inactive')
    return render_to_response('tournament/create.html',
        {'form': form},
        context_instance=RequestContext(request)
    )


@login_required()
def index_inactive(request):
    print 'index_inactive'
    return render_to_response('tournament/inactive.html',
        {'info' : Tournament.get_all_info(started=False)},
        context_instance=RequestContext(request)
    )


@login_required()
def details_inactive(request, tournament_id):
    info = get_object_or_404(Tournament, pk=tournament_id).get_info_tour()
    return render_to_response('tournament/details_inactive.html',
            {'info' : info},
        context_instance=RequestContext(request)
    )


@login_required()
def start_tournament(request, tournament_id):
    t = get_object_or_404(Tournament, pk = tournament_id, active=False)
    try:
        t.start_tournament()
        return redirect('Chess.apps.tournament.views.index')
    except ValidationError:
        message = Exception.message
        return HttpResponseRedirect('/tournaments/' + str(t.id) + '/inactive/')