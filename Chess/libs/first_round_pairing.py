# coding=utf-8

from Chess.apps.game.models import Game
from Chess.apps.player.models import PlayersInTournament
from random import randint, shuffle

__author__ = 'tstrinity'


class FirstRoundPairing():
    def __init__(self, tour):
        self.__tour = tour


    @staticmethod
    def __pairing_method_fold_pairing(sorted_players):
        """
        самый сильный с самым слабым
        """
        result = []
        for i in range(0,len(sorted_players) // 2):
            result.append(sorted_players[i])
            result.append(sorted_players[-(i+1)])
        return result


    @staticmethod
    def __pairing_method_slide_pairing(sorted_players):
        """
        игроки сортируются по рейтингу
        далее делятся на две равных комманды:
        первая половина и вторая
        матчи организовываются таким образом
        первый игрок из первой комманды - первый со второй комманды
        """
        team_amount = len(sorted_players) // 2
        result = []
        for i in range(team_amount):
            result.append(sorted_players[i])
            result.append(sorted_players[i + team_amount])
        return result


    @staticmethod
    def __pairing_method_adjacent_pairing(sorted_players):
        """
        первый со следующим и так далее
        """
        result = []
        players_count = len(sorted_players) // 2
        for i in range(0,players_count,2):
            result.append(sorted_players[i])
            result.append(sorted_players[i+1])
        return result


    @staticmethod
    def __pairing_method_random_pairing(sorted_players):
        """
        случайным образом
        """
        return shuffle(sorted_players)


    def create_pairs(self, pairing_method):
        players = self.__tour.tournament.player_set.all()
        sorted_players = sorted(players, key=lambda player: player.elo_rating, reverse = True)
        if not len(sorted_players) % 2 == 0:
            p_in_t = PlayersInTournament.objects.get(
                tournament = self.__tour.tournament,
                player = sorted_players[-1]
            )
            p_in_t.add_bye()
            sorted_players.remove(sorted_players[-1])
        if not pairing_method or pairing_method > 3:
            pairing_method = 0
        if pairing_method == 0: sorted_players = self.__pairing_method_fold_pairing(sorted_players)
        elif pairing_method == 1: sorted_players = self.__pairing_method_slide_pairing(sorted_players)
        elif pairing_method == 2: sorted_players = self.__pairing_method_adjacent_pairing(sorted_players)
        elif pairing_method == 3: sorted_players = self.__pairing_method_random_pairing(sorted_players)
        players_amount = len(sorted_players)
        first_player_color_white = randint(0,2)
        for i in range(0,players_amount, 2):
            g = Game(tour = self.__tour)
            g.save()
            white = bool(first_player_color_white) and i % 2 == 0
            g.add_player(sorted_players[i], white)
            g.add_player(sorted_players[i + 1], not white)