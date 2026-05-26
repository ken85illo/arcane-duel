import pygame
from enum import Enum, auto
from board import Board
from platform_sprite import Platform
from enums import GridConfig

# ===== HELPER FUNCTION ======
def tile_rect(row, col):
    # Get the rect from the tile
    return pygame.Rect(
        col * GridConfig.TILE_SIZE,
        row * GridConfig.TILE_SIZE,
        GridConfig.TILE_SIZE,
        GridConfig.TILE_SIZE,
    )

# ===== Helper functions =====
class BoardDisplay:
    def __init__(self, board, screen, player, ai, TILE_SIZE):
        self.player = player
        self.ai = ai
        
        self.TILE_SIZE = TILE_SIZE
        self.board = board
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 36) 
        
    def draw(self):
        self._draw_grid()

    def _draw_grid(self):
        overlay = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
        for row in range(GridConfig.GRID_SIZE):
            for col in range(GridConfig.GRID_SIZE):
                tile = self.board.get_tile(row, col)
                rect = tile_rect(row, col)

                text_surface = self.font.render(str(tile.mana), True, (255, 255, 255))
                self.screen.blit(text_surface, rect )
                self._draw_platform(row, col)

        # Draw player and AI once using correct coordinate mapping (col -> x, row -> y)
        player_row, player_col = self.board.player_pos
        self.player.draw(player_col * self.TILE_SIZE,player_row * self.TILE_SIZE, self.screen)

        ai_row, ai_col = self.board.ai_pos
        self.ai.draw(ai_col * self.TILE_SIZE, ai_row * self.TILE_SIZE,self.screen)
        
    def _draw_platform(self, row, col):
        platform_index = self._get_platform_index(row, col)
        # Map grid coordinates to screen coordinates: column -> x, row -> y
        x = col * self.TILE_SIZE
        y = row * self.TILE_SIZE

        is_dark = (row + col) % 2 == 0

        platform = Platform.get_platform(
            platform_index, self.TILE_SIZE, self.TILE_SIZE, is_dark=is_dark
        )
        self.screen.blit(platform, (x, y))

    def _get_platform_index(self, row, col):
        def is_platform(row, col):
            if self.board.is_in_bounds(row, col):
                return self.board.get_tile(row, col).is_active()
            return False

        if is_platform(row, col):
            return 0

        # Checks if the platform is surrounded by other platforms
        top = is_platform(row - 1, col)
        left = is_platform(row, col - 1)
        bottom = is_platform(row + 1, col)
        right = is_platform(row, col + 1)

        neighbor_map = {
            (True, True, True, True): 1,  # fully surrounded
            (True, True, True, False): 2,  # top, left, bottom
            (True, False, True, False): 3,  # top, bottom
            (True, False, True, True): 4,  # top, right, bottom
            (True, True, False, True): 5,  # top, left, right
            (True, True, False, False): 6,  # top, left
            (True, False, False, False): 7,  # top only
            (True, False, False, True): 8,  # top, right
            (False, True, False, True): 9,  # left, right
            (False, True, False, False): 10,  # left only
            (False, False, False, False): 11,  # fully empty
            (False, False, False, True): 12,  # right only
            (False, True, True, True): 13,  # left, bottom, right
            (False, True, True, False): 14,  # left, bottom
            (False, False, True, False): 15,  # bottom only
            (False, False, True, True): 16,  # right, bottom
        }

        key = (top, left, bottom, right)
        return neighbor_map.get(key)
        

        
    