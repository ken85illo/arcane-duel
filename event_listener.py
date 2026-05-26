from board_display import tile_rect
from enums import Phase
import pygame
import sys

class EventListener:
    def __init__(self, GRID_SIZE, current_phase):
        self.GRID_SIZE = GRID_SIZE
        self.current_phase = current_phase

    def _tile_at(self, px, py):
        # px, py reflects mouse position
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if tile_rect(row, col).collidepoint(px, py):
                    return row, col

        return None

    def events(self):
        mx, my = pygame.mouse.get_pos()
        print(f"{mx} {my}")

        # Tracks tile currently hovered at (future use: highlight tile selection) 
        self.hover_tile = self._tile_at(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    
            
            
            # When Game Over, restarts on 'R' key press
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.current_phase == Phase.GAME_OVER:
                self._new_game()
            
            # Handles left mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                print("PRESS")