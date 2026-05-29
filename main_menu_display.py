import pygame
from ui_util import PanelColors, GridConfig

class MainMenuDisplay:
    BUTTON_WIDTH = 260
    BUTTON_HEIGHT = 56

    def __init__(self, game):
        self.game = game

    def _create_buttons(self, x_pos, y_pos, width, height, color, text, text_size, text_color):
        button_rect = pygame.Rect(
            x_pos, y_pos, width, height,
        )

        # Default small text
        button_text = self.game.font_sm.render(text, True, text_color)

        if text_size == "sm":
            button_text = self.game.font_sm.render(text, True, text_color)

        elif text_size == "md":
            button_text = self.game.font_md.render(text, True, text_color)

        elif text_size == "lg":
            button_text = self.game.font_lg.render(text, True, text_color)
        
        pygame.draw.rect(self.game.screen, color, button_rect, border_radius=14)
        
        self.game.screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2))
        
        return button_rect
    

    def draw(self):
        SCREEN_W, SCREEN_H = self.game.screen.get_size()
        CENTER_X = SCREEN_W // 2

        self.game.screen.fill((12, 14, 30))
        
        title_text = self.game.font_xl.render("Arcane Duel", True, PanelColors.GOLD)
        subtitle_text = self.game.font_md.render("Monte Carlo Tree and BFS-Driven Strategy Game", True, PanelColors.TEXT_DIM)
        hint_text = self.game.font_sm.render("Choose an option to begin", True, PanelColors.TEXT_DIM)


        # GRID OPTION BUTTONS
        button_width = 100
        button_height = 40
        button_spacing = 20
        button_color = (255, 255, 255, 0)
        total_width = button_width * 3 + button_spacing * 2
        start_x = CENTER_X - total_width // 2
        button_y = SCREEN_H - 100

        self.sm_grid_button = self._create_buttons(x_pos=start_x, y_pos=button_y, 
                                                      width=button_width, height=button_height, 
                                                      color=button_color, text="5x5", 
                                                      text_size="md", text_color=(0,0,0))

        self.md_grid_button = self._create_buttons(x_pos=start_x + button_width + button_spacing, y_pos=button_y, 
                                                      width=button_width, height=button_height, 
                                                      color=button_color, text="7x7", 
                                                      text_size="md", text_color=(0,0,0))

        self.lg_grid_button = self._create_buttons(x_pos=start_x + (button_width + button_spacing) * 2, y_pos=button_y, 
                                                      width=button_width, height=button_height, 
                                                      color=button_color, text="9x9", 
                                                      text_size="md", text_color=(0,0,0))
        # BORDER
        # pygame.draw.rect(self.game.screen, PanelColors.WHITE, self.start_button, width=2, border_radius=14)

        self.game.screen.blit(title_text, (SCREEN_W // 2 - title_text.get_width() // 2, SCREEN_H // 2 - 120))
        self.game.screen.blit(subtitle_text, (SCREEN_W // 2 - subtitle_text.get_width() // 2, SCREEN_H // 2 - 72))
        self.game.screen.blit(hint_text, (SCREEN_W // 2 - hint_text.get_width() // 2, button_y + button_height + 18))

    def handle_click(self, mx, my):
        if self.sm_grid_button.collidepoint(mx, my):
            GridConfig.GRID_SIZE = 7
            self.game._new_game()
        elif self.md_grid_button.collidepoint(mx, my):
            GridConfig.GRID_SIZE = 9
            self.game._new_game()
        elif self.lg_grid_button.collidepoint(mx, my):
            GridConfig.GRID_SIZE = 11
            self.game._new_game()
