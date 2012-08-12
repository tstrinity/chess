# coding=utf-8

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.aggregates import Count
from Chess.libs.helpers import get_result_dic
from django.db import connection
from Chess.libs.helpers import timer
from django import forms

class Tournament(models.Model):
    name = models.CharField(max_length=50)
    prize_positions_amount = models.IntegerField(max_length=2)
    active = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    current_tour_number = models.IntegerField(default=0)
    signed_players = models.ManyToManyField(
        'player.Player',
        through='player.PlayersInTournament',
        blank = True
    )
    date = models.DateField(auto_now_add=True)


    class Meta:
        db_table = 'tournament'


    @staticmethod
    @timer
    def get_all_info(started):
        result = Tournament.objects.values('id','name','prize_positions_amount')\
            .filter(active=started)\
            .annotate(tours_amount = Count('_tours', distinct= True),
                players_amount = Count('_players', distinct = True))
        return result


    def start_tournament(self):
        if self.signed_players.count() > 1:
            self.active = True
            self.create_tours()
            self._tours.all()[0].create_games()
            self.save()
        else:
            raise ValidationError(message=u'Меньше чем два игрока подписано на турнир')


    def get_inactive_info(self):
        result = dict({
            'id' : self.id,
            'name': self.name,
            'prizes': self.prize_positions_amount,
            'players_count': self._players.count(),
            'players' : self.player_set.values('id', 'name', 'elo_rating')
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
        players_results = self._players.values('player__name', 'result')
        result = dict({
            'id' : self.id,
            'name': self.name,
            'prizes': self.prize_positions_amount,
            'players_count': self._players.count(),
            'tours_amount' : self._tours.count(),
            'tours_list': tours_list,
            'players_results': players_results
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
            tour = self._tours.create(tour_number=tours_number, tournament=self)
            tour.save()


    @timer
    def start_new_tour(self):
        self.current_tour_number += 1
        self.save()
        self._tours.all()[self.current_tour_number-1].create_games()



    def return_url(self):
        return '/tournaments/' + str(self.id) + '/'

    def __unicode__(self):
        return self.name


class TournamentAddForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        required=True,
        label=u'Название'
    )
    prize_positions_amount = forms.IntegerField(
        min_value=1,
        required=True,
        label=u'Количество призовых мест'
    )

    class Meta:
        model = Tournament
        fields = ('name', 'prize_positions_amount')