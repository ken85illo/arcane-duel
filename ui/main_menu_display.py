import pygame
import random
from ui.util import PanelColors, GridConfig

class MainMenuDisplay:
    BUTTON_WIDTH = 260
    BUTTON_HEIGHT = 56

    def __init__(self, game):
        self.game = game
        self.particles = [self._new_particle() for _ in range(60)]

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
    
    def _new_particle(self):
        sw, sh = self.game.screen.get_size()
        return {
            "x":     random.uniform(0, sw),
            "y":     random.uniform(0, sh),
            "vy":    random.uniform(-0.4, -1.2),
            "vx":    random.uniform(-0.3, 0.3),
            "r":     random.uniform(1.5, 4.0),
            "alpha": random.randint(40, 140),
            "col":   random.choice([(70,130,230),(180,90,220),(48,164,196),(255,210,55)]),
        }

    def _update_particles(self):
        sw, sh = self.game.screen.get_size()
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < -10 or p["x"] < -10 or p["x"] > sw + 10:
                p.update(self._new_particle())

    def draw(self):
        SCREEN_W, SCREEN_H = self.game.screen.get_size()
        CENTER_X = SCREEN_W // 2

        self.game.screen.fill((12, 14, 30))
        
        title_text = self.game.font_xl.render("ARCANE DUEL", True, PanelColors.GOLD)
        subtitle_text = self.game.font_md.render("Monte Carlo Tree and BFS-Driven Strategy Game", True, PanelColors.TEXT_DIM)
        grid_text = self.game.font_md.render("BOARD SIZE", True, PanelColors.TEXT_DIM)
        hint_text = self.game.font_sm.render("Choose an option to begin", True, PanelColors.TEXT_DIM)

        # GRID OPTION BUTTONS
        button_width = 100
        button_height = 40
        button_spacing = 20
        button_color = (255, 210,  55, 0)
        button_outline_color = (200, 155, 0, 0)
        total_width = button_width * 3 + button_spacing * 2
        start_x = CENTER_X - total_width // 2
        button_y = SCREEN_H - 255

        overlay = pygame.Surface((button_width, button_height), pygame.SRCALPHA)

        button_outline = pygame.Rect(start_x - 3.5, button_y - 3.5, button_width + 7, button_height + 7,)
        pygame.draw.rect(self.game.screen, button_outline_color, button_outline, border_radius=14)

        self.sm_grid_button = self._create_buttons(x_pos=start_x, y_pos=button_y, 
                                                      width=button_width, height=button_height, 
                                                      color=button_color, text="5x5", 
                                                      text_size="sm", text_color=(0,0,0))
        
        button_outline = pygame.Rect(start_x + button_width + button_spacing - 3.5, button_y - 3.5, button_width + 7, button_height + 7,)
        pygame.draw.rect(self.game.screen, button_outline_color, button_outline, border_radius=14)

        self.md_grid_button = self._create_buttons(x_pos=start_x + button_width + button_spacing, y_pos=button_y, 
                                                      width=button_width, height=button_height, 
                                                      color=button_color, text="7x7", 
                                                      text_size="sm", text_color=(0,0,0))

        button_outline = pygame.Rect(start_x + (button_width + button_spacing) * 2 - 3.5, button_y - 3.5, button_width + 7, button_height + 7,)
        pygame.draw.rect(self.game.screen, button_outline_color, button_outline, border_radius=14)

        self.lg_grid_button = self._create_buttons(x_pos=start_x + (button_width + button_spacing) * 2, y_pos=button_y, 
                                                      width=button_width, height=button_height, 
                                                      color=button_color, text="9x9", 
                                                      text_size="sm", text_color=(0,0,0))
        
        
        self.game.screen.blit(title_text, (SCREEN_W // 2 - title_text.get_width() // 2, SCREEN_H // 2 - 120))
        self.game.screen.blit(subtitle_text, (SCREEN_W // 2 - subtitle_text.get_width() // 2, SCREEN_H // 2 - 72))
        self.game.screen.blit(grid_text, (SCREEN_W // 2 - grid_text.get_width() // 2, button_y - 50))
        self.game.screen.blit(hint_text, (SCREEN_W // 2 - hint_text.get_width() // 2, SCREEN_H - 50))

        # Decorative line
        pygame.draw.line(self.game.screen, PanelColors.PANEL_LINE,
                         (CENTER_X - 200, button_y - 20), (CENTER_X + 200, button_y - 20), 1)

        pygame.draw.line(self.game.screen, PanelColors.PANEL_LINE,
                         (CENTER_X - 200, button_y + button_height + 15), (CENTER_X + 200, button_y + button_height + 15), 1)                         

        self.handle_hover(overlay)


        # Floating particles
        for p in self.particles:
            s = pygame.Surface((int(p["r"]*2), int(p["r"]*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["col"], p["alpha"]), (int(p["r"]), int(p["r"])), int(p["r"]))
            self.game.screen.blit(s, (int(p["x"]-p["r"]), int(p["y"]-p["r"])))

        self._update_particles()


    def handle_hover(self, overlay):
        color = (255, 255, 255,  100)

        mx, my = pygame.mouse.get_pos()
        if self.sm_grid_button.collidepoint(mx, my):
            overlay.fill(color)
            self.game.screen.blit(overlay, self.sm_grid_button)
        elif self.md_grid_button.collidepoint(mx, my):
            overlay.fill(color)
            self.game.screen.blit(overlay, self.md_grid_button)
        elif self.lg_grid_button.collidepoint(mx, my):
            overlay.fill(color)
            self.game.screen.blit(overlay, self.lg_grid_button)


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
