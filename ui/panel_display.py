from ui.util import GridConfig, PanelColors, draw_border, lerp
from core.enums import Phase, Spell, MageType
import pygame


class PanelDisplay:
    def __init__(self, game):
        self.game = game
        self.PANEL_WIDTH = game.PANEL_WIDTH
        self.panel_position_x = GridConfig.TILE_SIZE * GridConfig.GRID_SIZE


    def draw(self):
        pygame.draw.rect(self.game.screen, PanelColors.PANEL_FILL, pygame.Rect(self.panel_position_x, 0, self.PANEL_WIDTH, self.game.SCREEN_HEIGHT))
        pygame.draw.line(self.game.screen, PanelColors.PANEL_LINE, (self.panel_position_x, 0), (self.panel_position_x, self.game.SCREEN_HEIGHT), 2)        
        
        x_pos = self.panel_position_x + 14 
        y_pos = 12

        # Scorecards for each mage
        y_pos = self._score_card(x_pos, y_pos, MageType.PLAYER, self.game.board.player_mana, PanelColors.PLAYER, self.game.phase == Phase.PLAYER_MOVE or self.game.phase == Phase.PLAYER_SPELL)
        y_pos = self._score_card(x_pos, y_pos, MageType.AI, self.game.board.ai_mana, PanelColors.AI, self.game.phase == Phase.AI_MOVE or self.game.phase == Phase.AI_SPELL) 

        # Divider
        pygame.draw.line(self.game.screen, PanelColors.PANEL_LINE, (x_pos, y_pos), (x_pos + self.PANEL_WIDTH - 28, y_pos))
        y_pos += 10

        # Combat Log
        self._combat_log(x_pos, y_pos)

        # Spells 
        frozen, burn = self._btn_rects()

        can_afford_burn = self.game.board.can_afford_burn(MageType.PLAYER)
        is_player_turn = self.game.phase == Phase.PLAYER_SPELL

        self._spell_btn(frozen, Spell.FREEZE, is_player_turn, "Freeze (-0)", PanelColors.BTN_FRZ, True)
        self._spell_btn(burn, Spell.BURN, is_player_turn, "Burn (-3)", PanelColors.BTN_BURN, can_afford_burn)

        text = self.game.font_sm.render("Press [esc] to go to main menu", True, PanelColors.GOLD)
        self.game.screen.blit(text, (x_pos, 630))
    
    def _score_card(self, x, y, who, mana, color, is_active = False):
        height = 74
        card = pygame.Rect(x, y, self.PANEL_WIDTH - 28, height)
        bg_color = lerp(color, PanelColors.PANEL_FILL, 0.8) 

        draw_border(self.game.screen, bg_color, card, radius=10, width = 0)

        border_width = 3 if is_active else 2
        background_color  = color if is_active else lerp(color, PanelColors.PANEL_LINE, 0.8)
        draw_border(self.game.screen, background_color, card, radius=10, width=border_width)


        score_color = color
        if self.game.victory_lap_pending and self.game.victory_lap_pending[0] == who:
            score_color = (255, 255, 0)

        who_text = self.game.font_sm.render("PLAYER" if who == MageType.PLAYER else "AI", True, color)
        mana_score_text = self.game.font_xl.render(str(max(0, mana)), True, score_color)
        mana_caption_text = self.game.font_sm.render("mana", True, score_color)

        self.game.screen.blit(who_text, (x + 10, y + 7))
        self.game.screen.blit(mana_score_text, (x + 10, y + 24))       
        self.game.screen.blit(mana_caption_text, (x + 10 + mana_score_text.get_width() + 5, y + 44))

        return y + height + 10

    def _wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip() if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def _combat_log(self, x, y):
        lh2 = self.game.font_sm.render("COMBAT LOG", True, PanelColors.TEXT_DIM)
        self.game.screen.blit(lh2, (x, y))

        y += 18
        max_log_height = self.game.SCREEN_HEIGHT - 152 - y
        line_height = 16
        max_lines = max_log_height // line_height
        rendered_lines = []

        log_width = self.PANEL_WIDTH - 44

        for entry in self.game.log:
            text_color = PanelColors.TEXT

            if entry["src"] == MageType.PLAYER:
                text_color = PanelColors.PLAYER

            elif entry["src"] == MageType.AI:
                text_color = PanelColors.AI

            lb = self.game.font_sm.render(entry["msg"][:40], True, text_color)
            self.game.screen.blit(lb, (x, y))
            y += 16

    def _btn_rects(self):
        board_width = GridConfig.TILE_SIZE * GridConfig.GRID_SIZE 
        button_x = board_width + 12

        return (
            pygame.Rect(button_x, self.game.SCREEN_HEIGHT - 170, self.game.PANEL_WIDTH - 24, 50),
            pygame.Rect(button_x, self.game.SCREEN_HEIGHT -  102, self.game.PANEL_WIDTH - 24, 50)
        )

    def _spell_btn(self, rect, kind: Spell, phase_active, label, color, affordable):
        if not phase_active:
            # Not the spell phase: just show a dim placeholder
            draw_border(self.game.screen,PanelColors.BTN_DIM, rect, radius=10)
            
            text = self.game.font_md.render(label, True, PanelColors.TEXT_DIM)
            self.game.screen.blit(text, (rect.x + 10, rect.y + 16))
            return

        is_sel = self.game.spell_choice == kind

        if not affordable:
            # Can't afford this spell: greyed-out with "need 3" message
            draw_border(self.game.screen, (50, 30, 30), rect, radius=9)
            draw_border(self.game.screen, (100, 50, 50), rect, radius=9, width=2)
            text = self.game.font_md.render(label + " [need 3]", True, (120, 70, 70))
            self.game.screen.blit(text, (rect.x + 10, rect.y + 16))
            return

        # Normal active state: brighter if selected
        bg_color = lerp(color, (255, 255, 255), 0.25) if is_sel else lerp(color, PanelColors.PANEL_FILL, 0.35)
        border_color = (255, 255, 255) if is_sel else lerp(color, (255, 255, 255), 0.4)

        draw_border(self.game.screen, bg_color, rect, radius=9, width =0)
        draw_border(self.game.screen, border_color, rect, radius=9, width=2)
        
        text = self.game.font_md.render(label, True, PanelColors.WHITE if is_sel else PanelColors.WHITE)
        self.game.screen.blit(text, (rect.x + 10, rect.y + 14))

        

        

