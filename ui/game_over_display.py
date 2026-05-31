import pygame
from ui.util import PanelColors
from core.enums import MageType, Winner

class GameOverDisplay:
    def __init__(self, game):
        self.game = game

    def draw(self):
        SCREEN_W, SCREEN_H = self.game.screen.get_size()
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 185))
        self.game.screen.blit(ov, (0, 0))

        color = None
        text = ""

        # Setting Text Color based on Winner
        if self.game.winner == MageType.PLAYER:
            color = PanelColors.PLAYER
        
        elif self.game.winner == MageType.AI:
            color = PanelColors.AI

        else:
            color = PanelColors.GOLD

        # Setting Text based on Winner
        if self.game.winner != Winner.DRAW:
            winner = "Player" if self.game.winner == Winner.PLAYER else "AI"
            text = f"{winner} Wins!"

        else:
            text = "It's a Draw!"

        winner_text = self.game.font_xl.render(text, True, color)
        scores = f"Player: {self.game.board.player_mana} mana   |   AI: {self.game.board.ai_mana} mana"
        mana_scores_text = self.game.font_md.render(scores, True, PanelColors.TEXT)
        play_again_text = self.game.font_sm.render("Press  R  to play again", True, PanelColors.TEXT_DIM)
        
        self.game.screen.blit(winner_text, (SCREEN_W // 2 - winner_text.get_width() // 2, SCREEN_H // 2 - 80))
        self.game.screen.blit(mana_scores_text, (SCREEN_W // 2 - mana_scores_text.get_width() // 2, SCREEN_H // 2 - 4))
        self.game.screen.blit(play_again_text, (SCREEN_W // 2 - play_again_text.get_width() // 2, SCREEN_H // 2 + 40))
