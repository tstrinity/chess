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
        for tours_number in range(tours_count):
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
    game_result = models.IntegerField(max_length=1, blank= True)
    tour = models.ForeignKey('Tour', related_name='_games')
    signed_players = models.ManyToManyField(
        'Player',
        through='PlayersInGames',
    )

    def add_player(self, player):
        player_in_game = PlayersInGames(game=self, player=player)
        player_in_game.save()

    class Meta:
        db_table = 'game'


class PlayersInGames(models.Model):
    plays_white = models.BooleanField(blank=True)
    player = models.ForeignKey('Player', related_name='_games')
    game = models.ForeignKey('Game', related_name='_players')

    class Meta:
        db_table = 'players_in_games'
