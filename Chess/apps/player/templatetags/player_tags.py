# coding=utf-8

__author__ = 'tstrinity'

from django.template import Library

register = Library()

@register.simple_tag
def get_player_figure(white):
    if white:
        return '<img src="/static/img/chess-figure-white.png" style="width:30px;height:30px;">'
    else:
        return '<img src="/static/img/chess-figure-black.png" style="width:30px;height:30px;">'

@register.simple_tag
def get_winner_info(player_info):
    if player_info['game_result'] == 1:
        return get_player_figure(player_info['plays_white'])
    elif player_info['game_result'] == 3:
        return get_player_figure(not player_info['plays_white'])
    else:
        return u'Ничья'
