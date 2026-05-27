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

class AIState(Enum):
    THINKING = auto()
    MOVING = auto()
    CASTING_SPELL = auto()
    FINISHING_TURN = auto()

class Winner(Enum):
    PLAYER = auto()
    AI = auto()
    DRAW = auto()
    

    