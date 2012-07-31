__author__ = 'tstrinity'

from Chess.apps.tournament.models import *

t = Tournament(name = 'bilbo')
t.prize_positions_amount = 1
t.save()
for i in range(1,9):
    p = Player(name = 'Vasya' + str(i), elo_rating = 50*i)
    p.save()
    tp = PlayersInTournament(player = p, tournament=t)
    tp.save()
t.create_tours()
tr = t._tours.get(pk = 2)
tr.create_games()