# coding=utf-8
from django.db import models, connection
from Chess.libs.helpers import get_result_dic
from django import forms

__author__ = 'tstrinity'


class Player(models.Model):
    name = models.CharField(max_length=50, unique=True)
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

    @staticmethod
    def check_if_played(player1, player2):
        cursor = connection.cursor()
        cursor.execute("SELECT count(*) FROM\
                chess_db.player_in_game\
                INNER JOIN chess_db.player_in_game as g2\
                on chess_db.player_in_game.game_id = g2.game_id and\
                chess_db.player_in_game.player_id <> g2.player_id\
                where chess_db.player_in_game.player_id in (%s,%s) and\
                g2.player_id in (%s,%s);" ,
        [player1.player.id, player2.player.id,
         player1.player.id, player2.player.id]
        )
        result = get_result_dic(cursor)
        if result[0]['count(*)'] > 0:
            return True
        else:
            return False



class PlayerAddForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        required=True,
        label=u'Имя и фамилия игрока',
        error_messages={
            'unique': u'Такой игрок уже есть',
            'required': u'Вы не ввели имя и фамилию игрока',
            'max_length': u'Введите не более 50 символов'
        }
    )
    elo_rating = forms.IntegerField(
        max_value=5000,
        min_value=1,
        required=True,
        label=u'Эло рейтинг игрока',
        error_messages={
            'required': u'Вы не ввели рейтинг Эло игрока',
            'min_value': u'Рейтинг не может быть ниже 1',
            'max_value': u'Рейтинг не может быть больше 5000'
        }
    )

    class Meta:
        model = Player
        fields = ('name','elo_rating')


class ManyPlayersAddForm(forms.Form):
    players = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        tournament_id = kwargs.pop('tournament_id')
        super(ManyPlayersAddForm, self).__init__(*args, **kwargs)
        self.fields['players'].queryset = PlayersInTournament.objects.exclude(
            tournament_id = tournament_id
        ).values('players')