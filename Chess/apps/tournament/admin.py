
__author__ = 'tstrinity'

from django.contrib import admin
from Chess.apps.tournament.models import *


class TourInline(admin.StackedInline):
    model = Tour
    fields = ['tour_number']
    readonly_fields = ['tour_number']


class PlayersInTournamentsInline(admin.TabularInline):
    model = PlayersInTournament
    extra = 1


class PlayerInline(admin.TabularInline):
    model = Player


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

admin.site.register(Tournament,TournamentAdmin)