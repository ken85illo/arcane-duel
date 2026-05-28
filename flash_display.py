import pygame
from ui_util import GridConfig, PanelColors

class FlashDisplay:
    def __init__(self, game):
        self.game = game

    def draw(self):
        surf = pygame.Surface((GridConfig.TILE_SIZE * GridConfig.GRID_SIZE, 70), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 160))
        self.game.screen.blit(surf, (0, 0))
        text = self.game.font_xl.render(self.game.flash_msg, True, PanelColors.GOLD)
        self.game.screen.blit(
            text,
            (
                GridConfig.TILE_SIZE * GridConfig.GRID_SIZE // 2 - text.get_width() // 2,
                15,
            ),
        )