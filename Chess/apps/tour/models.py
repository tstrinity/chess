# coding=utf-8

from django.db import models
from Chess.apps.player.models import  PlayersInGames
from Chess.libs.helpers import timer

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
            from Chess.libs.first_round_pairing import FirstRoundPairing
            pairing = FirstRoundPairing(self)
            pairing.create_pairs(self.tournament.pairing_method_first)
        else:
            from Chess.libs.burstein_swiss_pairing import BursteinSwissPairing
            pairing = BursteinSwissPairing(self)
            pairing.create_pairs()


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
        return u'Тур ' + str(self.tour_number) + u' - ' + self.tournament.name
