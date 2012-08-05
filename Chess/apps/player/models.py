from django.db import models

__author__ = 'tstrinity'


class Player(models.Model):
    name = models.CharField(max_length=50)
    elo_rating = models.IntegerField(max_length=4, db_index = True)
    signed_to_tournaments = models.ManyToManyField(
        'tournament.Tournament',
        through = 'PlayersInTournament',
        blank = True
    )
    played_games = models.ManyToManyField('game.Game',
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
    tournament = models.ForeignKey('tournament.Tournament' ,related_name='_players')

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


class PlayersInGames(models.Model):
    GAME_RESULTS = (
        (0, 'not played') ,
        (1, 'loose'),
        (2, 'draw'),
        (3, 'win'),
        )
    plays_white = models.BooleanField(blank=True)
    game_result = models.IntegerField(choices = GAME_RESULTS, default = 0)
    player = models.ForeignKey('player.Player', related_name='_games')
    game = models.ForeignKey('game.Game', related_name='_players')


    class Meta:
        db_table = 'player_in_game'