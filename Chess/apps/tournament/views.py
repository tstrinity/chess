from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext
from Chess.apps.tournament.models import Tournament, TournamentAddForm
from Chess.apps.player.models import PlayerAddForm, ManyPlayersAddForm, PlayersInTournament
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
    sign_new_player_form = PlayerAddForm(request.POST or None)
    sign_existing_players = ManyPlayersAddForm(request.POST or None)
    if request.method == 'POST':
        if 'button_sign_new' in request.POST:
            if sign_new_player_form.is_valid():
                player = sign_new_player_form.save()
                p_in_t = PlayersInTournament(player = player, tournament_id = tournament_id)
                p_in_t.save()
                sign_new_player_form = PlayerAddForm()
        elif 'button_sign_existing' in request.POST:
            if sign_new_player_form.is_valid():
                pass
    info = get_object_or_404(Tournament, pk=tournament_id).get_inactive_info()
    return render_to_response('tournament/details_inactive.html', {
        'info' : info,
        'sign_new' : sign_new_player_form,
        'sign_existing' : sign_existing_players
        }, context_instance=RequestContext(request)
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