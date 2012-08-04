# coding=utf-8

from django.db import models
from Chess.apps.game.models import Game
from Chess.apps.player.models import PlayersInTournament, PlayersInGames
from Chess.libs.first_round_pairing import create_pairs
from Chess.libs.helpers import timer
from Chess.libs.tour import sort_players_by_results

__author__ = 'tstrinity'

class Tour(models.Model):
    """
    реализует модель тура в турнире
    поля: количество туров, внешний ключ турнира
    индекс по внешнему ключу ключу турнира
    """
    tour_number = models.IntegerField(max_length=2)
    tournament = models.ForeignKey('tournament.Tournament', related_name='_tours')


    class Meta:
        db_table = 'tour'


    def __unicode__(self):
        return u'Тур ' + str(self.tour_number)


    @timer
    def create_games(self):
        """
        если первый тур сортируем игроков по рейтингу
            если количество нечетное то самого низкого по рейтингу
            добавляем как проходящего в след. тур с одним очком
            иначе
        """
        if self.tour_number == 1:
            create_pairs(self,  0)
        else:
            p_in_t  = PlayersInTournament.objects.filter(
                tournament = self.tournament
            )
            sorted_players = sort_players_by_results(p_in_t)
            team_amount = len(sorted_players) // 2
            for i in range(team_amount):
                g = Game(tour = self)
                g.save()
                g.add_player(sorted_players[i], True)
                g.add_player(sorted_players[i + team_amount], False)


    @timer
    def get_games_info(self):
        result = []
        games = self._games.all()
        for g in games:
            temp = {
                'id' : g.id,
                'finished' : g.finished
            }
            players_info = PlayersInGames.objects.filter(game = g)
            temp['players_info'] = players_info.values('plays_white','game_result','player__name')
            result.append(temp)
        return result