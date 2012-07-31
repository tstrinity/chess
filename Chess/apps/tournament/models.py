# coding=utf-8

from django.db import models
from django.db.models.aggregates import Count
from helpers import get_result_dic
from django.db import connection

def timer(f):
    def _timer(*args, **kwargs):
        import time
        t = time.time()
        result = f(*args, **kwargs)
        print "Time: %f" % (time.time()-t)
        return result
    return _timer

class Tournament(models.Model):
    name = models.CharField(max_length=50)
    prize_positions_amount = models.IntegerField(max_length=2)
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
    def get_info(self):
        tours = []
        for tour in self._tours.filter(_games__count > 0):
            temp = dict({
                'id' : tour.pk,
                'number': tour.tour_number,
                'game_count': tour._games.count()
            })
            tours.append(temp)
        result = dict({
            'name': self.name,
            'prizes': self.prize_positions_amount,
            'players_count': self._players.count(),
            'tours_list': tours
        })
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
            'name': self.name,
            'prizes': self.prize_positions_amount,
            'players_count': self._players.count(),
            'tours_amount' : self._tours.count(),
            'tours_list': tours_list
        })
        return result



    def create_tours(self):
        player_amount = self._players.count()
        from Chess.libs.tour import calculate_tours_amount
        tours_amount = calculate_tours_amount(player_amount, self.prize_positions_amount)
        for tours_number in range(1, tours_amount + 1):
            tour = Tour(tour_number=tours_number, tournament=self)
            tour.save()

    def __unicode__(self):
        return self.name


class Tour(models.Model):
    """
    реализует модель тура в турнире
    поля: количество туров, внешний ключ турнира
    индекс по внешнему ключу ключу турнира
    """
    tour_number = models.IntegerField(max_length=2)
    tournament = models.ForeignKey(Tournament, related_name='_tours')

    class Meta:
        db_table = 'tour'

    def __unicode__(self):
        return u'Тур ' + str(self.tour_number)

    def create_games(self):
        if self.tour_number == 1:
            from Chess.libs.elo_rating import sort_players
            sorted_players = sort_players(self.tournament.player_set.all())
            team_amount = len(sorted_players) // 2
            for i in range(team_amount):
                g = Game(tour = self)
                g.save()
                g.add_player(sorted_players[i], True)
                g.add_player(sorted_players[i+team_amount], False)


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

    def __unicode__(self):
        return self.name

    class Meta:
        db_table =  'player'


class PlayersInTournament(models.Model):
    result = models.FloatField(default = 0.0)
    player = models.ForeignKey(Player, related_name='_tournaments')
    tournament = models.ForeignKey(Tournament,related_name='_players')

    class Meta:
        db_table = 'player_in_tournament'

    def add_draw(self):
        self.result += 0.5

    def add_win(self):
        self.result += 1


class Game(models.Model):
    finished = models.BooleanField(default = False)
    tour = models.ForeignKey('Tour', related_name ='_games')
    signed_players = models.ManyToManyField(
        'Player',
        through='PlayersInGames',
    )

    class Meta:
        db_table = 'game'

    def add_player(self, player, plays_white):
        player_in_game = PlayersInGames(
            game = self,
            player = player,
            plays_white = plays_white)
        player_in_game.save()

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
