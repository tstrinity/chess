# coding=utf-8

__author__ = 'tstrinity'

from Chess.apps.player.models import PlayersInGames
from Chess.apps.game.models import Game

def create_pairs(tour):
    players = tour.tournament._players.all()
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
            if popped_player:
                group.insert(0, popped_player)
                popped_player = None
                if not proceed_group(group):
                    #запоминаем текущую группу для дальнейшего мерджа
                    merge_group = group
        else:
            popped_player = group.pop()


def create_game(player1, player2):
    #добавить тур
    g = Game()
    g.add_player(player1, True)
    g.add_player(player2, False)
    g.save()


def proceed_group(group):
    if amount_is_even(group):
        i = 1
        while group.count() > 0:
            if i == len(group):
                return False
            if players_not_met_before(group[0],group[-i]):
                create_game(group[0], group[-i])
                group.remove(group[0])
                group.remove(group[-i])
            else:
                i += 1


def create_sub_groups(players):
    result = {}
    for player_data in players:
        if not result.has_key(player_data.result):
            result[player_data.result] = []
        result[player_data.result].append(player_data.player)
    return result


def amount_is_even(group):
    if group.count() % 2 == 0:
        return True
    else:
        return False



def players_not_met_before(player1, player2):
    return True