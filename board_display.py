import pygame
from enum import Enum, auto
from board import Board
from platform_sprite import Platform

class BoardDisplay:
    def __init__(self, board, screen, TILE_SIZE):
        self.TILE_SIZE = TILE_SIZE
        self.board = board
        self.screen = screen
        
    def draw(self):
        self._draw_grid()

    def _draw_grid(self ):
        overlay = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)

        for row in range(Board.GRID_SIZE):
            for col in range(Board.GRID_SIZE):
                tile = self.board.get_tile(row, col)

                self._draw_active(row, col, )

    
    def _draw_active(self, row, col):
        x = row * self.TILE_SIZE
        y = col * self.TILE_SIZE

        is_dark = (row + col) % 2 == 0

        platform = Platform.get_platform(
            0, self.TILE_SIZE, self.TILE_SIZE, is_dark=is_dark
        )
        self.screen.blit(platform, (x, y))

        
    