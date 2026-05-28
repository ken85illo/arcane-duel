import pygame
from enum import Enum, auto
from board import Board
from platform_sprite import Platform
from enums import Direction, MageType, Phase, Spell
from ui_util import GridConfig, HighlightColors, draw_border, lerp, tile_rect

class BoardDisplay:
    def __init__(self, game):
        self.game = game
        self.TILE_SIZE = GridConfig.TILE_SIZE

        
    def draw(self):
        self._draw_grid()

    def _draw_grid(self):
        game = self.game
        overlay = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)

        for row in range(GridConfig.GRID_SIZE):
            for col in range(GridConfig.GRID_SIZE):
                tile = game.board.get_tile(row, col)
                rect = tile_rect(row, col)
                text = self.game.font_md.render(str(tile.mana), True, (255, 255, 255))

                self._draw_platform(row, col)

                if tile.is_active() or tile.is_frozen():
                    self.game.screen.blit(text, rect)
                    self._draw_active_tile_overlay(row, col, rect, overlay)


        self._draw_mages()


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
            new_x, new_y = player_col * self.TILE_SIZE,player_row * self.TILE_SIZE 

        game.player.draw(new_x, new_y, game.board.player_direction == Direction.LEFT, game.screen)


        # Play the AI animation for movement
        if ai_anim:
            new_x, new_y = ai_anim.current_pixel()
        else:
            new_x, new_y = ai_col * self.TILE_SIZE,ai_row * self.TILE_SIZE 

        game.ai.draw(new_x, new_y, game.board.ai_direction == Direction.LEFT, game.screen)

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
        x = col * self.TILE_SIZE
        y = row * self.TILE_SIZE

        is_frozen = game.board.get_tile(row, col).is_frozen()
        is_dark = (row + col) % 2 == 0

        platform = Platform.get_platform(
            platform_index, self.TILE_SIZE, self.TILE_SIZE, is_dark=is_dark, is_frozen=is_frozen
        )
        game.screen.blit(platform, (x, y))

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





        
        
    
