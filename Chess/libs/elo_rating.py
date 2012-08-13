# coding=utf-8

__author__ = 'tstrinity'

def get_k_factor(rating):
    """
    функция для возвращения коэффициента опыта играка
    взяты значения для интернет соревнований
    """
    if rating < 2100:
        return 32
    elif rating < 2400:
        return 24
    else:
        return 16


def get_mo(first_player_rating, second_player_rating):
    """
    расчет мат. ожидания количества очков которое наберет игрок в партии
    исходные данные рейтинг первого игрока и его противника
    """
    mo_first_player = 1 / (1 + pow(10, (
        (second_player_rating - first_player_rating) / 400)
    ))
    return mo_first_player

def get_new_elo_rating(p_in_t, players):
    """
    рассчитывает новый Эло рейтинг игрока
    исходные данные рейтинг игрока и список игр
    влючающий рейтинг противника и результат
    """
    total_mo = 0
    total_score = 0
    for p_in_t in players:
        total_mo += get_mo(p_in_t.player.elo_rating, p_in_t.player.elo_rating)
        total_score += p_in_t.result
    new_rating = p_in_t.player.elo_rating + get_k_factor(p_in_t.player.elo_rating) * (
        total_score - total_mo
    )
    return new_rating

