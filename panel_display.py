from enums import GridConfig
import pygame

class PanelColors:
    PANEL_FILL = (20, 22, 40)
    PANEL_LINE = (50, 54, 88)
    

class PanelDisplay:
    def __init__(self, game):
        self.game = game
        self.PANEL_WIDTH = game.PANEL_WIDTH
        self.panel_position_x = GridConfig.TILE_SIZE * GridConfig.GRID_SIZE
        
    def draw(self):
        pygame.draw.rect(self.game.screen, PanelColors.PANEL_FILL, pygame.Rect(self.panel_position_x, 0, self.PANEL_WIDTH, self.game.SCREEN_HEIGHT))
        pygame.draw.line(self.game.screen, PanelColors.PANEL_LINE, (self.panel_position_x, 0), (self.panel_position_x, self.game.SCREEN_HEIGHT), 2)        
        
        