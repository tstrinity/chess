# coding=utf-8

__author__ = 'tstrinity'

from Chess.apps.player.models import PlayersInGames, PlayersInTournament

class BursteinSwissPairing():
    def __init__(self, tour):
        self.__tour = tour
        self.__popped_player = None

    def __create_game(self, player1, player2, player1_plays_white):
        g = self.__tour._games.create()
        g.add_player(player1, player1_plays_white)
        g.add_player(player2, not player1_plays_white)
        g.save()


    def __proceed_group(self, group):
        i = 1
        while len(group) > 1:
            if i == len(group):
                #в группе нет игрока с которым текущий рассматриваемый
                #игрок может сыграть партию
                return False
            if not PlayersInGames.check_if_played(group[0].player, group[-i].player, self.__tour.tournament_id):
                p1_in_t = PlayersInTournament.objects.get(player_id = group[0].player.id,
                    tournament_id = self.__tour.tournament_id)
                p2_in_t = PlayersInTournament.objects.get(player_id = group[-i].player.id,
                    tournament_id = self.__tour.tournament_id)
                if p1_in_t.due_color + p2_in_t.due_color in range(-3,+4):
                    self.__create_game(group[0].player, group[-i].player,  self.__get_p1_color(group[0], group[-i]))
                    group.remove(group[0])
                    group.remove(group[-i])
                    i = 1
            else:
                i += 1
        if len(group) == 1:
            self.__popped_player = group.pop()
        return True


    def __get_p1_color(self, p1, p2):
        if abs(p1.due_color) == 2:
            p1_white = return_if_white(p1.due_color)
            return p1_white
        elif abs(p2.due_color) == 2:
            p1_white = not return_if_white(p2.due_color)
            return p1_white
        else:
            p1_white = return_if_white(p1.due_color)
            return p1_white


    def __sort_group_by_buhgolz(self, group):
        group_with_buhgolz = []
        for player in group:
            rating = get_buhgolz(
                player = player.player,
                tournament = self.__tour.tournament
            )
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
        result = []
        for player in sorted_players:
            result.append(player['p_in_t'])
        return result


    def create_pairs(self):
        players = self.__tour.tournament._players.all()
        groups = create_sub_groups(players)
        #получаем список отсортированных по убыванию ключей груп
        group_keys = sorted(groups.keys(), reverse = True)
        popped_player = None
        merge_group = None
        for group_key in group_keys:
            group = groups[group_key]
            if merge_group:
                group += merge_group
            if len(group) > 1 or popped_player:
                if self.__popped_player:
                    group.insert(0, self.__popped_player)
                    self.__popped_player = None
                    group = self.__sort_group_by_buhgolz(group)
                if not self.__proceed_group(group):
                #запоминаем текущую группу для дальнейшего мерджа
                    merge_group = group
                    groups.pop(group_key)

            else:
                self.__popped_player = group.pop()
        if len(groups.values()) == 1:
            player = groups.values()[0]
            p_in_t = PlayersInTournament.objects.get(player = player, tournament = self.__tour.tournament)
            p_in_t.add_bye()



def return_if_white(due_color):
    if due_color <= 0:
        return True
    if due_color > 0:
        return False


def create_sub_groups(players):
    result = {}
    for player_data in players:
        if not result.has_key(player_data.result):
            result[player_data.result] = []
        result[player_data.result].append(player_data)
    return result


def amount_is_even(group):
    if group.count() % 2 == 0:
        return True
    else:
        return False


def get_buhgolz(player, tournament):
    player = PlayersInTournament.objects.get(player = player, tournament = tournament)
    enemies = player.played_with()
    sum_rating = 0
    for enemy in enemies:
        sum_rating += enemy.result
    return  sum_rating
