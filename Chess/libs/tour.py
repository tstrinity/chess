# coding=utf-8

__author__ = 'tstrinity'

from math import log

def calculate_tours_count(players_count, prize_positions):
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