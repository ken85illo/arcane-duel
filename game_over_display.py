import pygame
from ui_util import PanelColors

class GameOverDisplay:
    def __init__(self, game):
        self.game = game

    def draw(self):
        SCREEN_W, SCREEN_H = self.game.screen.get_size()
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 185))
        self.game.screen.blit(ov, (0, 0))

        col = (
            PanelColors.PLAYER
            if self.game.winner == "Blue Mage"
            else (PanelColors.AI if self.game.winner == "Red Mage" else PanelColors.GOLD)
        )
        txt = (
            f"{self.game.winner} Wins!" if self.game.winner != "Draw" else "It's a Draw!"
        )

        t = self.game.font_xl.render(txt, True, col)
        self.game.screen.blit(
            t, (SCREEN_W // 2 - t.get_width() // 2, SCREEN_H // 2 - 80)
        )

        sc = self.game.font_md.render(
            f"Blue: {self.game.board.player_mana} mana   |   Red: {self.game.board.ai_mana} mana",
            True,
            PanelColors.TEXT,
        )
        self.game.screen.blit(
            sc, (SCREEN_W // 2 - sc.get_width() // 2, SCREEN_H // 2 - 4)
        )

        rr_lbl = self.game.font_sm.render(
            "Press  R  to play again", True, PanelColors.TEXT_DIM
        )
        self.game.screen.blit(
            rr_lbl,
            (SCREEN_W // 2 - rr_lbl.get_width() // 2, SCREEN_H // 2 + 40),
        )
