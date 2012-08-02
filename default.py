__author__ = 'tstrinity'

from Chess.apps.tournament.models import *

t = Tournament(name = 'deutschland')
t.prize_positions_amount = 1
t.save()
for i in range(1,25):
    p = Player(name = 'Vasya' + str(i), elo_rating = 50*i)
    p.save()
    tp = PlayersInTournament(player = p, tournament = t)
    tp.save()
t.create_tours()
tr = t._tours.all()[0]
tr.create_games()