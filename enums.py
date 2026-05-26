from enum import Enum, auto

class MageType(Enum):
    PLAYER = auto()
    AI = auto()

class Spell(Enum):
    BURN = auto()
    FREEZE = auto()   

class Phase(Enum):
    PLAYER_MOVE = auto()
    PLAYER_SPELL = auto()
    AI_MOVE = auto()
    AI_SPELL = auto()
    GAME_OVER = auto()

class TileState(Enum):
    ACTIVE = auto()
    EMPTY = auto()
    FROZEN = auto()
    WALL = auto()

class GridConfig:
    TILE_SIZE = 80
    GRID_SIZE = 11
    