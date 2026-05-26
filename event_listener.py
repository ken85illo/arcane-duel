from board_display import tile_rect
from enums import Phase, GridConfig
import pygame
import sys

class EventListener:
    def __init__(self, board, current_phase, valid_moves_set):
        self.board = board
        self.current_phase = current_phase
        self.valid_moves_set = valid_moves_set

    def _tile_at(self, px, py):
        # px, py reflects mouse position
        for row in range(GridConfig.GRID_SIZE):
            for col in range(GridConfig.GRID_SIZE):
                if tile_rect(row, col).collidepoint(px, py):

                    return row, col

        return None

    def events(self):
        mx, my = pygame.mouse.get_pos()

        # Tracks tile currently hovered at (future use: highlight tile selection) 
        self.hover_tile = self._tile_at(mx, my)
        print(f"Hovering over tile: {self.hover_tile}")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    
            
            # When Game Over, restarts on 'R' key press
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.current_phase == Phase.GAME_OVER:
                self._new_game()
            
            # Handles left mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.current_phase == Phase.PLAYER_MOVE:
                    self._handle_player_click(mx, my)
    
    def _handle_player_click(self, mx, my):
        clicked_tile = self._tile_at(mx, my)

        if self.current_phase == Phase.PLAYER_MOVE and clicked_tile in self.valid_moves_set:
            row, col = clicked_tile
            self.board.apply_move(Mage.PLAYER, row, col)
            print(f"Player moved to ({row}, {col})")

