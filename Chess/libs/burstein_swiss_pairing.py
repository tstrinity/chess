__author__ = 'tstrinity'

def create_pairs(players):
    pass


def create_sub_groups(players):
    result = {}
    for player_data in players:
        if not result.has_key(player_data.result):
            result[player_data.result] = []
        result[player_data.result].append(player_data.player)
    return result