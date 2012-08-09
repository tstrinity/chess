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
            from Chess.libs.burstein_swiss_pairing import create_pairs
            create_pairs(self)


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



    class Meta:
        db_table = 'tour'


    def __unicode__(self):
        return u'Тур ' + str(self.tour_number)
