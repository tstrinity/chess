# coding=utf-8

__author__ = 'tstrinity'

from math import log

def calculate_tours_amount(players_count, prize_positions):
    """
    функция для рассчета количество туров в турнире
    исходные данные: количество участников, количество призовых мест
    если количество призовых мест == 1 правая часть формулы не вычисляется
    """
    left, right = 0,0
    if prize_positions < 1 | players_count < 2:
        raise ValueError()
    left = round(log(players_count, 2))
    if (prize_positions != 1):
        right = round(log(prize_positions - 1, 2))
    return int(left + right)

def sort_players(players):
    sorted_players = sorted(players, key=lambda player: player.elo_rating, reverse = True)
    return sorted_players

def sort_players_by_results(p_in_t):
    print p_in_t
    sorted_p_in_t = sorted(p_in_t, key=lambda item: item.result, reverse= True)
    sorted_players = []
    for item in sorted_p_in_t:
        sorted_players.append(item.player)
    return sorted_players
