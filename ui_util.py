import pygame

class GridConfig:
    TILE_SIZE = 80
    GRID_SIZE = 11

# ===== PANEL COLORS ====
class PanelColors:
    # Panel Color
    PANEL_FILL = (20, 22, 40)
    PANEL_LINE = (50, 54, 88)

    # Mage Colors
    PLAYER    = ( 70, 130, 230)  # Blue Mage (player)
    AI        = (220,  55,  55)  # Red Mage (AI)

    # UI text and button colours
    GOLD      = (255, 210,  55)  
    TEXT      = (220, 220, 228)  
    TEXT_DIM  = (118, 118, 145)  
    BTN_FRZ   = ( 40, 160, 210)  
    BTN_BURN  = (200,  65,  30)  
    BTN_DIM   = ( 38,  40,  65)  
    WHITE     = (255, 255, 255)
    BLACK     = (  0,   0,   0)

    

# ===== HIGHLIGHT COLORS ======
class HighlightColors:
    MOVE_FILL = (220, 160, 20, 65)
    MOVE_BORDER = (240, 180, 30)

    SPELL_FILL = (230, 50, 230, 60)  
    SPELL_BORDER = (255, 100, 255)  

    HOVER_FILL= (255, 255, 255,  45)


def draw_border(screen, color, rect, radius=10, width=2):
    pygame.draw.rect(screen, color, rect, width, border_radius=radius)


def _make_font(self, size, bold=False):
    for name in ("dejavusans", "liberationsans", "freesans", "droidsans"):
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            pass
    return pygame.font.Font(None, size + 6)  # Fall back to pygame's built-in bitmap font


def lerp(first_color, second_color, factor):
    # Linearly interpolate between two colors by factor
    return tuple(int(first_color[i] + (second_color[i] - first_color[i]) * factor) for i in range(3))