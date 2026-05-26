from enum import Enum, auto
import random
import sys
from tile import Tile
from board import Board
from board_display import BoardDisplay

import pygame


class Phase(Enum):
    PLAYER_MOVE = auto()
    PLAYER_SPELL = auto()
    AI_MOVE = auto()
    AI_SPELL = auto()

class Game:
    TILE_SIZE = 60

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Arcane Duel")
        self.screen = pygame.display.set_mode ((self.TILE_SIZE * 10, self.TILE_SIZE * 10))
        self.clock = pygame.time.Clock()
        self._new_game()
    
    # ===== Game Setup =====
    def _new_game(self):
        self.board = Board() # Starting board
        self.board_display = BoardDisplay(self.board, self.screen, self.TILE_SIZE)
        self.phase = self._randomize_starting_turn() # Starting turn
        self.hover_tile   = None # Grid position under the mouse cursor
        self.valid_player_movev_set = set() # Valid movement targets for the player this turn
        self.valid_player_spell_set = set() # Valid spell targets for the player this turn
        self.spell_choice = None # Which spell the player selected (freeze/burn)
        self.winner = None           # "Blue Mage", "Red Mage", or "Draw"

        # == To Be Added
        # self.log = [] # Combat log entries (max 9 lines)
        # self.flash_msg    = ""             # Short message shown in the center of the board
        # self.flash_timer  = 0             # How many frames the flash message remains visible
        # self.ai_busy      = False

    def _randomize_starting_turn(self) -> Phase:
        r = random.randint(1, 100)

        return Phase.PLAYER_MOVE if r <= 50 else Phase.AI_MOVE
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.board_display.draw()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    Game().run()
        
    
    






