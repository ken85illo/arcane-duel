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
    MAIN_MENU = auto()

class TileState(Enum):
    ACTIVE = auto()
    EMPTY = auto()
    FROZEN = auto()
    WALL = auto()

class AIState(Enum):
    START = auto()
    THINKING = auto()
    MOVING = auto()
    CASTING_SPELL = auto()
    FINISHING_TURN = auto()

class Winner(Enum):
    PLAYER = auto()
    AI = auto()
    DRAW = auto()
    
class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()    

class MenuBoardSize(Enum):
    FIVE_BY_FIVE = auto()
    SEVEN_BY_SEVEN = auto()
    NINE_BY_NINE = auto()

class MenuDifficulty(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()