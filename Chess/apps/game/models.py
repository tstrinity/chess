# coding=utf-8
from django.db import models, connection
from Chess.apps.player.models import PlayersInGames, PlayersInTournament
from Chess.libs.helpers import timer, get_result_dic

__author__ = 'tstrinity'


class Game(models.Model):
    finished = models.BooleanField(default = False, verbose_name=u'Окончена')
    tour = models.ForeignKey('tour.Tour', related_name ='_games', verbose_name=u'Тур')
    signed_players = models.ManyToManyField(
        'player.Player',
        through='player.PlayersInGames',
        verbose_name=u'Игроки'
    )

    class Meta:
        db_table = 'game'
        verbose_name = u'Игра'
        verbose_name_plural = u'Игры'

    def __unicode__(self):
        players = self._players.all()
        p1_name = players[0].player.name
        p2_name = players[1].player.name
        return self.tour.tournament.name + ' : ' + p1_name + ' - ' + p2_name


    @timer
    def add_player(self, player, plays_white):
        """
        добавляет участника в игру, и меняет его предпочтительный цвет
        """
        player_in_game = PlayersInGames(
            game = self,
            player = player,
            plays_white = plays_white,
            tournament_id = self.tour.tournament.id
        )
        player_in_game.save()
        player_in_tournament = PlayersInTournament.objects.get(
            tournament = self.tour.tournament,
            player = player
        )
        if plays_white:
            if player_in_tournament.due_color in [0,1]:
                player_in_tournament.due_color += 1
            else:
                player_in_tournament.due_color = 1
        else:
            if player_in_tournament.due_color in [0, -1]:
                player_in_tournament.due_color -= 1
            else:
                player_in_tournament.due_color = -1
        player_in_tournament.save()


    @timer
    def get_game_data(self):
        """
        возвращает данные об игре
        """
        players = self.signed_players.all()
        cursor = connection.cursor()
        cursor.execute("SELECT\
            chess_db.player.name,\
            chess_db.player.elo_rating,\
            chess_db.players_in_games.plays_white,\
            chess_db.players_in_games.game_result\
            FROM chess_db.players_in_games\
            INNER JOIN chess_db.player\
            ON chess_db.players_in_games.player_id = chess_db.player.id\
            WHERE game_id = %s AND player_id = %s OR player_id = %s;  " ,
            [self.id, players[0].id, players[1].id]
        )
        return  get_result_dic(cursor)


    @timer
    def set_match_result(self, result):
        """
        выставляет результат в матче
        если все матчи в туре завершены запускает новый тур
        """
        self.finished = True
        self.save()
        tournament = self.tour.tournament
        if result == 'draw':
            for player_in_game in self._players.all():
                player_in_game.game_result = 2
                player_in_game.save()
                pg = PlayersInTournament.objects.get(player = player_in_game.player,
                    tournament = tournament)
                pg.add_draw()
        else:
            winner = self._players.get(player__name = result)
            winner.game_result = 3
            winner.save()
            pg = PlayersInTournament.objects.get(player = winner.player, tournament = tournament)
            pg.add_win()
            looser = self._players.exclude(player = winner.player).get()
            looser.game_result = 1
            looser.save()
            pg = PlayersInTournament.objects.get(player = looser.player,
                tournament = tournament)
            pg.add_loose()
        if not len(self.tour._games.filter(finished=False)):
            return self.tour.tournament.start_new_tour()
        return False