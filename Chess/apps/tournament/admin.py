from django.contrib.sites.models import Site
from Chess.apps.player.models import PlayersInTournament, Player, PlayersInGames
from Chess.apps.tour.models import Tour
from Chess.apps.game.models import Game

__author__ = 'tstrinity'

from django.contrib import admin
from Chess.apps.tournament.models import *


class TourInline(admin.StackedInline):
    model = Tour
    fields = ['tour_number']
    readonly_fields = ['tour_number']


class PlayersInTournamentsInline(admin.TabularInline):
    model = PlayersInTournament


class PlayerInGamesInline(admin.TabularInline):
    model = PlayersInGames

class PlayerInline(admin.TabularInline):
    model = Player


class GameAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInGamesInline,
    ]

    fields = ['tour']
    readonly_fields = ['tour']

    def has_add_permission(self, request):
        return False


class PlayerAdmin(admin.ModelAdmin):
    inlines = [
        PlayersInTournamentsInline,
    ]


class TournamentAdmin(admin.ModelAdmin):
    inlines = [
        TourInline,
        PlayersInTournamentsInline,
        ]
    readonly_fields = ['prize_positions_amount']

admin.site.unregister(Site)
admin.site.register(Tournament,TournamentAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Player)