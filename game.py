import random
import sys

from enums import Phase
from event_listener import EventListener
from board import Board
from board_display import BoardDisplay, tile_rect
from mage import Mage, MageStates
from board import Board
from enums import MageType, GridConfig, Spell
import pygame

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Arcane Duel")
        self.screen = pygame.display.set_mode (
            (GridConfig.TILE_SIZE * GridConfig.GRID_SIZE, GridConfig.TILE_SIZE * GridConfig.GRID_SIZE))

        self.clock = pygame.time.Clock()
        self._new_game()
    
    # ===== Game Setup =====
    def _new_game(self):
        self.player = Mage(False)
        self.ai = Mage(True)
        self.player.set_state(MageStates.ATTACK)

        self.board = Board() # Starting board
        self.board_display = BoardDisplay(self.board, self.screen, self.player, self.ai,  GridConfig.TILE_SIZE)
        self.hover_tile   = None # Grid position under the mouse cursor
        self.valid_player_move_set = set() # Valid movement targets for the player this turn
        self.valid_player_spell_set = set() # Valid spell targets for the player this turn
        self.phase =  Phase.PLAYER_MOVE # self._randomize_starting_turn() # Starting turn
        self.event_listener = EventListener(self.board, self.phase, self.valid_player_move_set)
        self.spell_choice = None
        self.winner = None     
        # == To Be Added
        # self.log = [] # Combat log entries (max 9 lines)
        # self.flash_msg    = ""             # Short message shown in the center of the board
        # self.flash_timer  = 0             # How many frames the flash message remains visible
        # self.ai_busy      = False

        self.update_valid_moves()
        self.update_valid_spells()

    def _randomize_starting_turn(self) -> Phase:
        r = random.randint(1, 100)

        return Phase.PLAYER_MOVE if r <= 50 else Phase.AI_MOVE

    # State helpers section

    def update_valid_moves(self):
        row, col = self.board.player_pos
        self.valid_player_move_set = self.board.valid_mage_moves(row, col)

    def update_valid_spells(self):
        row, col = self.board.player_pos
        self.valid_player_spell_set = self.board.valid_spell_targets(row, col)

    # ===== Action Listeners =====
    def _tile_at(self, px, py):
        # px, py reflects mouse position
        for row in range(GridConfig.GRID_SIZE):
            for col in range(GridConfig.GRID_SIZE):
                if tile_rect(row, col).collidepoint(px, py):

                    return row, col

        return None

    def _events(self):
        mx, my = pygame.mouse.get_pos()

        # Tracks tile currently hovered at (future use: highlight tile selection) 
        self.hover_tile = self._tile_at(mx, my)
        is_inside_val = self.hover_tile in self.valid_player_move_set
        # print(self.valid_player_move_set)
        # print(f"Player pos: {self.board.player_pos}\nHovering over tile: {self.hover_tile} inside {is_inside_val}")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    
            
            # When Game Over, restarts on 'R' key press
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.phase == Phase.GAME_OVER:
                self._new_game()
            
            # Handles left mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.phase == Phase.PLAYER_MOVE or self.phase == Phase.PLAYER_SPELL:
                    self._handle_player_click(mx, my)
    
    def _handle_player_click(self, mx, my):
        clicked_tile = self._tile_at(mx, my)

        if self.phase == Phase.PLAYER_MOVE and clicked_tile in self.valid_player_move_set:
            row, col = clicked_tile
            self.board.apply_move(MageType.PLAYER, row, col)
            self.update_valid_spells()
            self.phase = Phase.PLAYER_SPELL # Transition to spell phase after a move
            print(f"Player moved to {clicked_tile}. Valid spells: {self.valid_player_spell_set}")
        
        elif self.phase == Phase.PLAYER_SPELL and clicked_tile in self.valid_player_spell_set:
            row, col = clicked_tile
            self.board.apply_spell(MageType.PLAYER, Spell.FREEZE, row, col)
            self.update_valid_spells()


    # ===== Main Game Loop =====
    def run(self):
        while True:
            self._events()
            self.board_display.draw()
            
            pygame.display.flip()
            self.clock.tick(60)
            self.player.update()
            self.ai.update()

if __name__ == "__main__":
    Game().run()
        
    
    






