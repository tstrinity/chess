from django.db import models

class Tournament(models.Model):
    name = models.CharField(max_length=50)
    prize_positions_count = models.IntegerField(max_length=2)
    tours_count = models.IntegerField(max_length=2, blank = True)
    signed_players = models.ManyToManyField('Player', through='PlayersInTournament', blank = True)


    class Meta:
        db_table = 'Tournaments'

class Tour(models.Model):
    tour_number = models.IntegerField(max_length=2)
    tournament = models.ForeignKey(Tournament, related_name='tours')

    class Meta:
        db_table = 'Tours'


class Player(models.Model):
    name = models.CharField(max_length=50)
    elo_rating = models.IntegerField(max_length=4)
    signed_to_tournaments = models.ManyToManyField(Tournament,
        through = 'PlayersInTournament',
        blank = True
    )

    def __unicode__(self):
        return self.name

class PlayersInTournament(models.Model):
    result = models.DecimalField(max_digits=3,decimal_places=1)
    player = models.ForeignKey(Player, related_name='players')
    tournament = models.ForeignKey(Tournament,related_name='tournaments')

    class Meta:
        db_table = 'PlayersInTournaments'

    def add_draw(self):
        self.result += 0.5

    def add_win(self):
        self.result += 1



class Game(models.Model):

    game_ended = models.DateTimeField(auto_now_add = True)
    game_result = models.IntegerField(max_length=1)
    player1 = models.OneToOneField(Player, related_name='player1')
    player2 = models.OneToOneField(Player, related_name='player2')

