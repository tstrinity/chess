# coding=utf-8

from django.db import models

class Tournament(models.Model):
    name = models.CharField(max_length=50)
    prize_positions_count = models.IntegerField(max_length=2)
    signed_players = models.ManyToManyField(
        'Player',
        through='PlayersInTournament',
        blank = True
    )
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'tournaments'

    def create_tours(self):
        player_count = self._players.count()
        from Chess.libs.tour import calculate_tours_count
        tours_count = calculate_tours_count(player_count, self.prize_positions_count)
        for tours_number in range(1, tours_count + 1):
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
        db_table = 'tours'

    def __unicode__(self):
        return u'Тур ' + str(self.tour_number)

    def create_games(self):
        if self.tour_number == 1:
            from Chess.libs.elo_rating import sort_players
            sorted_players = sort_players(self.tournament.player_set.all())
            team_count = len(sorted_players) // 2
            for i in range(team_count):
                g = Game(tour = self)
                g.save()
                g.add_player(sorted_players[i], True)
                g.add_player(sorted_players[i+team_count], False)



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
        db_table = 'players_in_tournaments'

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
        from django.db import connection, transaction
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
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]


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
        db_table = 'players_in_games'
