import random
import sys

from enums import Phase
from event_listener import EventListener
from board import Board
from board_display import BoardDisplay
from mage import Mage, MageStates

import pygame

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
        self.player = Mage(False, 200, 200)
        self.player.set_state(MageStates.SIDE_WALK_LEFT)
        self.ai = Mage(True)
        self.board = Board() # Starting boa:w
        self.board_display = BoardDisplay(self.board, self.screen, self.TILE_SIZE)
        self.phase = self._randomize_starting_turn() # Starting turn
        self.event_listener = EventListener(10, self.phase)
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

    # State helpers section

    # --------------------

    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.event_listener.events()
            self.board_display.draw()
            self.player.draw(100, 100, self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
            self.player.update()

if __name__ == "__main__":
    Game().run()
        
    
    






