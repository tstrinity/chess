# coding=utf-8

__author__ = 'tstrinity'

from Chess.apps.player.models import PlayersInGames, PlayersInTournament
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
                #sort_by_buhgolz(gruop)
            if not proceed_group(group, tour):
                    #запоминаем текущую группу для дальнейшего мерджа
                merge_group = group
        else:
            popped_player = group.pop()


def create_game(player1, player2, player1_plays_white, tour):
    g = tour._games.create()
    g.add_player(player1, player1_plays_white)
    g.add_player(player2, not player1_plays_white)
    g.save()


def proceed_group(group, tour):
    i = 1
    while len(group) > 1:
        if i == len(group):
            return False
        if not PlayersInGames.check_if_played(group[0].player, group[-i].player, tour.tournament_id):
            p1_in_t = PlayersInTournament.objects.get(player_id = group[0].player.id,
                tournament_id = tour.tournament_id)
            p2_in_t = PlayersInTournament.objects.get(player_id = group[-i].player.id,
                tournament_id = tour.tournament_id)
            if p1_in_t.due_color + p2_in_t.due_color in range(-3,+4):
                create_game(group[0].player, group[-i].player, get_p1_color(group[0], group[-i]), tour)
                group.remove(group[0])
                group.remove(group[-i])
        else:
            i += 1


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

def get_p1_color(p1, p2):
    if abs(p1.due_color) == 2:
        p1_white = return_if_white(p1.due_color)
        return p1_white
    elif abs(p2.due_color) == 2:
        p1_white = not return_if_white(p2.due_color)
        return p1_white
    else:
        p1_white = return_if_white(p1.due_color)
        return p1_white


def return_if_white(due_color):
    if due_color <= 0:
        return True
    if due_color > 0:
        return False


def get_buhgolz(player, tournament):
    player = PlayersInTournament.objects.get(player = player, tournament = tournament)
    enemies = player.played_with()
    sum_rating = 0
    for enemy in enemies:
        sum_rating += enemy.result
    return  sum_rating
