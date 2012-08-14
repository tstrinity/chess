# coding=utf-8
from django.contrib.sites.models import Site
from Chess.apps.player.models import PlayersInTournament, Player, PlayersInGames
from Chess.apps.tour.models import Tour
from Chess.apps.game.models import Game

__author__ = 'tstrinity'

from django.contrib import admin
from Chess.apps.tournament.models import *


class TourInline(admin.StackedInline):
    model = Tour
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class PlayersInTournamentsInline(admin.TabularInline):
    model = PlayersInTournament

    verbose_name = u'Участник'
    verbose_name_plural = u'Участники'

    readonly_fields = ['tournament']

    def has_add_permission(self, request):
        return False



class PlayerInGamesInline(admin.TabularInline):
    model = PlayersInGames
    readonly_fields = ['plays_white', 'player']
    exclude = ['tournament_id']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class PlayerInline(admin.TabularInline):
    model = Player


class GameAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInGamesInline,
    ]

    fields = ['tour', 'finished']
    readonly_fields = ['tour','finished']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PlayerAdmin(admin.ModelAdmin):
    inlines = [
        PlayersInTournamentsInline,
    ]


class TournamentAdmin(admin.ModelAdmin):
    inlines = [
        PlayersInTournamentsInline,
    ]

    readonly_fields = ['prize_positions_amount', 'finished', 'current_tour_number', 'pairing_method_first' ]

    def has_add_permission(self, request):
        return False

admin.site.unregister(Site)
admin.site.register(Tournament,TournamentAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Player)