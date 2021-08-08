from enum import Enum


class Games(Enum):
    APEX = 'apex'
    FORTNITE = 'fortnite'
    COD_WARZONE = 'warzone'
    VALORANT = 'valorant'
    CSGO = 'csgo'


game_squad_sizes = {
    'apex': 3,
    'fortnite': 4,
    'warzone': 3,
    'valorant': 5,
    'csgo': 5
}
