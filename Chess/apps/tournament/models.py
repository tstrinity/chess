# coding=utf-8

from django.db import models
from django.db.models.aggregates import Count
from Chess.libs.helpers import get_result_dic
from django.db import connection
from Chess.libs.tour import sort_players, sort_players_by_results
from Chess.libs.helpers import timer

class Tournament(models.Model):
    name = models.CharField(max_length=50)
    prize_positions_amount = models.IntegerField(max_length=2)
    finished = models.BooleanField(default=False)
    current_tour_number = models.IntegerField(default=0)
    signed_players = models.ManyToManyField(
        'Player',
        through='PlayersInTournament',
        blank = True
    )
    date = models.DateField(auto_now_add=True)


    class Meta:
        db_table = 'tournament'


    @staticmethod
    @timer
    def get_tournaments_info():
        cursor = connection.cursor()
        cursor.execute("SELECT\
            chess_db.tournament.name,\
            chess_db.tournament.prize_positions_amount,\
            (SELECT COUNT(*) FROM chess_db.player_in_tournament\
            WHERE chess_db.tournament.id = player_in_tournament.tournament_id) AS players_amount,\
            (SELECT COUNT(*) FROM tour WHERE tour.tournament_id = chess_db.tournament.id) AS tours_amount\
            FROM  chess_db.tournament"
        )
        return  get_result_dic(cursor)


    @staticmethod
    @timer
    def get_all_info():
        result = Tournament.objects.values('id','name','prize_positions_amount')\
            .annotate(tours_amount = Count('_tours', distinct= True),
                players_amount = Count('_players', distinct = True))
        return result


    @timer
    def get_info_tour(self):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM\
                (SELECT *,\
                    (SELECT count(*) FROM  chess_db.game\
                    WHERE chess_db.tour.id = chess_db.game.tour_id) AS game_amount,\
                    (SELECT count(*) FROM  chess_db.game WHERE\
                    chess_db.tour.id = chess_db.game.tour_id\
                        and chess_db.game.finished = True) AS game_done_amount\
                FROM chess_db.tour) AS T\
                WHERE T.game_amount > 0 AND tournament_id = %s;" ,
        [self.id]
        )
        tours_list = get_result_dic(cursor)
        result = dict({
            'id' : self.id,
            'name': self.name,
            'prizes': self.prize_positions_amount,
            'players_count': self._players.count(),
            'tours_amount' : self._tours.count(),
            'tours_list': tours_list
        })
        return result


    @timer
    def get_players_ratings(self):
        return  self._players.values('player__name', 'games_played', 'result').order_by('-result')


    @timer
    def create_tours(self):
        player_amount = self._players.count()
        from Chess.libs.tour import calculate_tours_amount
        tours_amount = calculate_tours_amount(player_amount, self.prize_positions_amount)
        for tours_number in range(1, tours_amount + 1):
            tour = Tour(tour_number=tours_number, tournament=self)
            tour.save()


    @timer
    def start_new_tour(self):
        self.current_tour_number += 1
        self._tours.all()[self.current_tour_number].create_games()
        self.save()


    def return_url(self):
        return '/tournaments/' + str(self.id) + '/'

    def __unicode__(self):
        return self.name


class Tour(models.Model):
    """
    реализует модель тура в турнире
    поля: количество туров, внешний ключ турнира
    индекс по внешнему ключу ключу турнира
    """
    tour_number = models.IntegerField(max_length=2)
    tournament = models.ForeignKey('Tournament', related_name='_tours')


    class Meta:
        db_table = 'tour'


    def __unicode__(self):
        return u'Тур ' + str(self.tour_number)


    @timer
    def create_games(self):
        if self.tour_number == 1:
            sorted_players = sorted(players, key=lambda player: player.elo_rating, reverse = True)
            if not len(sorted_players) % 2 == 0:
                p_in_t = PlayersInTournament.objects.get(
                    tournament = self.tournament,
                    player = sorted_players[-1]
                )
                p_in_t.add_bye()

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


class Player(models.Model):
    name = models.CharField(max_length=50)
    elo_rating = models.IntegerField(max_length=4, db_index = True)
    signed_to_tournaments = models.ManyToManyField(
        'Tournament',
        through = 'PlayersInTournament',
        blank = True
    )
    played_games = models.ManyToManyField('Game',
        through='PlayersInGames',
        blank = True
    )

    @staticmethod
    def get_elo_ratings():
        return  Player.objects.values('name', 'elo_rating')

    def __unicode__(self):
        return self.name


    class Meta:
        db_table =  'player'


class PlayersInTournament(models.Model):
    result = models.FloatField(default = 0.0)
    games_played = models.IntegerField(default=0)
    due_color = models.IntegerField(default=0)
    has_bye = models.BooleanField(default=False)
    player = models.ForeignKey('Player', related_name='_tournaments')
    tournament = models.ForeignKey('Tournament' ,related_name='_players')

    class Meta:
        db_table = 'player_in_tournament'


    def add_bye(self):
        self.has_bye = True
        self.save()


    def add_draw(self):
        self.result += 0.5
        self.games_played += 1
        self.save()


    def add_win(self):
        self.result += 1
        self.games_played += 1
        self.save()


    def add_loose(self):
        self.games_played += 1
        self.save()


class Game(models.Model):
    finished = models.BooleanField(default = False)
    tour = models.ForeignKey('Tour', related_name ='_games')
    signed_players = models.ManyToManyField(
        'Player',
        through='PlayersInGames',
    )

    class Meta:
        db_table = 'game'


    @timer
    def add_player(self, player, plays_white):
        player_in_game = PlayersInGames(
            game = self,
            player = player,
            plays_white = plays_white)
        player_in_game.save()


    @timer
    def get_game_data(self):
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
        self.finished = True
        self.save()
        tournament = Tour.objects.get(pk = self.tour_id).tournament
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
        if self.tour._games.filter(finished = False).count() == 0:
            self.tour.tournament.start_new_tour()
            return True
        return False


class PlayersInGames(models.Model):
    GAME_RESULTS = (
        (0, 'not played') ,
        (1, 'loose'),
        (2, 'draw'),
        (3, 'win'),
    )
    plays_white = models.BooleanField(blank=True)
    game_result = models.IntegerField(choices = GAME_RESULTS, default = 0)
    player = models.ForeignKey('Player', related_name='_games')
    game = models.ForeignKey('Game', related_name='_players')

    class Meta:
        db_table = 'player_in_game'
