import pygame
from enum import Enum, auto
from board import Board
from platform_sprite import Platform
from enums import Direction, MageType, Phase, Spell, Winner
from tile import Tile
from ui_util import GridConfig, HighlightColors, draw_border, lerp, tile_rect

class BoardDisplay:
    def __init__(self, game):
        self.game = game
        self.victory_lap_tiles = []
        self.victory_lap_player = None

    def draw(self):
        self._draw_grid()
        self._draw_victory_lap()
        self._draw_freeze_anims()
        self._draw_mages()
        self._draw_fire_anims()

    def _draw_grid(self):
        game = self.game
        overlay = pygame.Surface((GridConfig.TILE_SIZE, GridConfig.TILE_SIZE), pygame.SRCALPHA)

        for row in range(GridConfig.GRID_SIZE):
            for col in range(GridConfig.GRID_SIZE):
                tile = game.board.get_tile(row, col)
                rect = tile_rect(row, col)

                self._draw_platform(row, col)

                if tile.is_active() or tile.is_frozen():
                    if not tile.is_cumulative:
                        color = (37, 76, 39) 
                    else:
                        mana_text_colors = [
                            (25, 45, 120),   # Dark Blue
                            (40, 35, 140),
                            (60, 30, 160),
                            (85, 25, 180),
                            (115, 20, 200),  # Dark Purple
                        ]
                        color = mana_text_colors[tile.mana - 1] 
                        
                    text = self.game.font_lg.render(str(tile.mana), True, color)
                    self.game.screen.blit(text, rect)

                    self._draw_active_tile_overlay(row, col, rect, overlay)

                if tile.is_frozen():
                    self._draw_cumul_bar(rect, tile.freeze_timer, Tile.FREEZE_TILE_TIMER, (160, 220, 255), (40, 70, 100))

    def _draw_mages(self):
        game = self.game

        # Find active animations
        player_anim = next((anim for anim in game.move_anims if anim.who == MageType.PLAYER), None)
        ai_anim = next((anim for anim in game.move_anims if anim.who == MageType.AI), None)

        player_row, player_col = game.board.player_pos
        ai_row, ai_col = game.board.ai_pos

        # Play the player animation for movement
        if player_anim:
            new_x, new_y = player_anim.current_pixel()
        else:
            new_x, new_y = player_col * GridConfig.TILE_SIZE, player_row * GridConfig.TILE_SIZE

        game.player.draw(new_x, new_y, game.board.player_direction == Direction.LEFT, game.screen)


        # Play the AI animation for movement
        if ai_anim:
            new_x, new_y = ai_anim.current_pixel()
        else:
            new_x, new_y = ai_col * GridConfig.TILE_SIZE, ai_row * GridConfig.TILE_SIZE

        game.ai.draw(new_x, new_y, game.board.ai_direction == Direction.LEFT, game.screen)
    
    
    def _draw_victory_lap(self):
        if self.game.victory_lap_pending and self.game.victory_lap_pending[2]:
            self.victory_lap_tiles.append(self.game.victory_lap_pending[2].pop())
            self.victory_lap_player = self.game.victory_lap_pending[0]
        
        if self.victory_lap_player == MageType.PLAYER:
            color = (0, 0, 255, 100)
        else:
            color = (255, 0, 0, 100)

        for tile in self.victory_lap_tiles:
            rect = tile_rect(*tile)
            effect = pygame.Surface((GridConfig.TILE_SIZE, GridConfig.TILE_SIZE), pygame.SRCALPHA)
            effect.fill(color)
            self.game.screen.blit(effect, rect.topleft)    
        
            
    
    def _draw_fire_anims(self):
        for anim in self.game.fire_anims:
            if anim.frame <= anim.FALL_END:
                anim.draw(self.game.screen)
            elif anim.frame <= anim.IMPACT_END:
                impact_frame = anim.impact_frame()
                alpha = int(200 * (1 - impact_frame))
                rect = tile_rect(*anim.target_pos)

                if alpha > 0:
                    effect = pygame.Surface((GridConfig.TILE_SIZE, GridConfig.TILE_SIZE), pygame.SRCALPHA)
                    effect.fill((255, int(80*(1-impact_frame)), 0, alpha))
                    self.game.screen.blit(effect, rect.topleft)    

    def _draw_freeze_anims(self):
        for anim in self.game.freeze_anims:
            if anim.frame <= anim.FREEZE_END:
                freeze_frame = anim.freeze_frame()
                alpha = int(200 * (1 - freeze_frame))
                rect = tile_rect(*anim.target_pos)

                if alpha > 0:
                    effect = pygame.Surface((GridConfig.TILE_SIZE, GridConfig.TILE_SIZE), pygame.SRCALPHA)
                    effect.fill((40, 160, int(210*(1-freeze_frame)), alpha))
                    self.game.screen.blit(effect, rect.topleft)    
        

    def _draw_active_tile_overlay(self, row, col, rect, overlay):
        game = self.game

        # Highlight the possible movements for player
        if game.phase == Phase.PLAYER_MOVE and (row, col) in game.valid_player_move_set:
            overlay.fill(HighlightColors.MOVE_FILL)
            game.screen.blit(overlay, rect.topleft)
            draw_border(game.screen, HighlightColors.MOVE_BORDER, rect)
        elif self.game.spell_choice and game.phase == Phase.PLAYER_SPELL and (row, col) in game.valid_player_spell_set:
            if self.game.spell_choice == Spell.FREEZE and self.game.board.get_tile(row, col).is_frozen():
                return

            overlay.fill(HighlightColors.SPELL_FILL)
            game.screen.blit(overlay, rect.topleft)
            draw_border(game.screen, HighlightColors.SPELL_BORDER, rect)


        if (row, col) == game.hover_tile:
            overlay.fill(HighlightColors.HOVER_FILL)
            game.screen.blit(overlay, rect.topleft)

        
    def _draw_platform(self, row, col):
        game = self.game
        platform_index = self._get_platform_index(row, col)

        # Map grid coordinates to screen coordinates: column -> x, row -> y
        x = col * GridConfig.TILE_SIZE
        y = row * GridConfig.TILE_SIZE

        tile =game.board.get_tile(row, col)
        is_frozen = tile.is_frozen()
        is_dark = (row + col) % 2 == 0
        is_cumulative = tile.is_cumulative

        platform = Platform.get_platform(
            platform_index, GridConfig.TILE_SIZE, GridConfig.TILE_SIZE, is_dark=is_dark, is_frozen=is_frozen, is_cumulative=is_cumulative
        )
        game.screen.blit(platform, (x, y))

    def _draw_cumul_bar(self, rect, value, max, fill_color, bg_color, border_radius=5):
        value = min(value, max)
        pos_x, pos_y = rect.x + 8, rect.bottom - 20
        bar_width, bar_height = rect.width - 16, 10
        pygame.draw.rect(self.game.screen, bg_color, (pos_x, pos_y, bar_width, bar_height), border_radius=border_radius)
        fill = int(bar_width * (value / max))
        if fill > 0:
           pygame.draw.rect(self.game.screen, fill_color, (pos_x, pos_y, fill, bar_height), border_radius=border_radius) 

        draw_border(self.game.screen, bg_color, pygame.Rect(pos_x, pos_y, bar_width, bar_height), radius=border_radius, width=3)


    def _get_platform_index(self, row, col):
        def is_platform(row, col):
            if self.game.board.is_in_bounds(row, col):
                tile = self.game.board.get_tile(row, col)
                return tile.is_active() or tile.is_frozen()
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





        
        
    
