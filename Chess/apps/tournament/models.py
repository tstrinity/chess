# coding=utf-8

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.aggregates import Count
from Chess.apps.player.models import PlayersInTournament
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


    def get_winners_info(self):
        """
        возращает список выйгравшних
        """
        result = self._players.all().order_by('-result').\
            values('player__name', 'result')[:self.prize_positions_amount]
        return result


    @timer
    def get_players_ratings(self):
        """
        рейтинг игроков в турнире
        """
        return  self._players.values('player__name', 'games_played', 'result', 'result_position').order_by('-result')


    @staticmethod
    @timer
    def get_all_info(started):
        """
        возвращает сводку по турниру
        """
        result = Tournament.objects.values('id','name','prize_positions_amount','finished')\
            .filter(active=started)\
            .annotate(tours_amount = Count('_tours', distinct= True),
                players_amount = Count('_players', distinct = True))
        return result


    def start_tournament(self):
        """
        запуск турнира
        """
        if self.signed_players.count() > 1:
            self.active = True
            self.create_tours()
            self._tours.all()[0].create_games()
            self.save()
        else:
            raise ValidationError(message=u'Меньше чем два игрока подписано на турнир')


    def get_inactive_info(self):
        """
        возврщает данные неактивного турнира
        """
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
        """
        возврщает информацию по турниру
        его хар-ки и список туров
        """
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
            'finished': self.finished,
            'players_count': self._players.count(),
            'tours_amount' : self._tours.count(),
            'tours_list': tours_list,
        })
        return result


    @timer
    def create_tours(self):
        """
        расчет количества туров и создание
        """
        player_amount = self._players.count()
        from Chess.libs.tour import calculate_tours_amount
        tours_amount = calculate_tours_amount(player_amount, self.prize_positions_amount)
        for tours_number in range(1, tours_amount + 1):
            tour = self._tours.create(tour_number=tours_number, tournament=self)
            tour.save()


    @timer
    def start_new_tour(self):
        """
        переход к следующему туру
        """
        if self.current_tour_number > self._tours.count():
            self.finished = True
            self.save()
            self.sign_winners()
            return False
        else:
            self.current_tour_number += 1
            self.save()
            self._tours.all()[self.current_tour_number].create_games()
            return True



    def calculate_new_elo_rating(self):
        from Chess.libs.elo_rating import get_new_elo_rating
        all_players = self._players.select_related(depth = 1)
        result = []
        for p_in_t in all_players:
            new_rating = get_new_elo_rating(p_in_t, p_in_t.played_with())
            item = {'player' : p_in_t.player, 'new_rating' : new_rating }
            result.append(item)
        for item in result:
            item['player'].elo_rating = item['new_rating']
            item['player'].save()



    def sign_winners(self):
        from Chess.libs.burstein_swiss_pairing import get_buhgolz
        all_players = PlayersInTournament.objects.filter(tournament = self)
        sorted_players = sorted(all_players, key = lambda player: player.result, reverse = True)
        from Chess.libs.burstein_swiss_pairing import create_sub_groups
        groups = create_sub_groups(sorted_players)
        group_keys = sorted(groups.keys(), reverse = True)
        current_prize_position = 1
        for group_key in group_keys:
            group = groups[group_key]
            group_with_buhgolz = []
            for player in group:
                rating = get_buhgolz(player = player.player, tournament = self)
                group_with_buhgolz.append(
                    {
                        'buhgolz' : rating,
                        'p_in_t' : player
                    }
                )
            sorted_players = sorted(group_with_buhgolz,
                key= lambda item: item['buhgolz'],
                reverse=True
            )
            for item in sorted_players:
                item['p_in_t'].result_position = current_prize_position
                item['p_in_t'].save()
                current_prize_position += 1







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