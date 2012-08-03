# coding=utf-8

__author__ = 'tstrinity'


def sort_pairs(sorted_players, pairing_method):
    '''
    сортировка в зависимости от выбранного метода
    '''
    if pairing_method > 3:
        pairing_method = 0
    if pairing_method == 0: return pairing_method_fold_pairing(sorted_players)
    if pairing_method == 1: return pairing_method_slide_pairing(sorted_players)
    if pairing_method == 2: return pairing_method_adjacent_pairing(sorted_players)
    if pairing_method == 3: return pairing_method_slide_pairing(sorted_players)

def pairing_method_fold_pairing(players):
    '''
    самый сильный с самым слабым противником
    '''
    pass



def pairing_method_slide_pairing():
    pass

def pairing_method_adjacent_pairing():
    pass

def pairing_method_random_pairing():
    pass

def first_round_color_picker():
    pass