import random
import sys
from mage import Mage
from enum import Enum, auto

import pygame
from platform_sprite import Platform


class MapGrid:
    # 10 rows (y), 11 columns (x)
    MAP = [
        ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
        ["x", " ", " ", " ", "p", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x"],
        ["x", " ", " ", " ", " ", "b", " ", " ", " ", " ", "x"],
        ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
    ]


class TurnState(Enum):
    PLAYER_MOVE = auto()
    PLAYER_SPELL = auto()
    BOT_MOVE = auto()
    BOT_SPELL = auto()


class SpellOption(Enum):
    BURN = auto()
    FREEZE = auto()

class Game:
    TILE_SIZE = 60

    # TEMPORARY COLORS. WILL BE CHANGED WITH SPRITES.
    COLOR_WALL = (40, 40, 50)
    COLOR_PLAYER = (255, 255, 255)
    COLOR_BOT = (251, 116, 168)
    COLOR_OBJECT = (115, 194, 251)
    COLOR_FLOOR = (29, 28, 42)

    # UI Constants
    UI_PANEL_HEIGHT = 60
    COLOR_UI_BG = (20, 20, 30)
    COLOR_BTN_ACTIVE = (230, 90, 40)  # Orange-Red for Burn
    COLOR_BTN_INACTIVE = (60, 60, 80)
    COLOR_BTN_FREEZE = (70, 150, 230)  # Ice Blue for Freeze

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Arcane Duel")

        self.map = [row[:] for row in MapGrid.MAP]
        self.rows = len(self.map)
        self.cols = len(self.map[0])

        self.grid_width = self.cols * self.TILE_SIZE
        self.grid_height = self.rows * self.TILE_SIZE

        # Total screen dimensions: Add space at bottom for buttons
        self.width = self.grid_width
        self.height = self.grid_height + self.UI_PANEL_HEIGHT

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        self.freeze_coords ={
            "player": {
                "x": None,
                "y": None
            }, 

            "bot": {
                "x": None,
                "y": None
            }, 
        }

        self.player_x = 4
        self.player_y = 1

        self.bot_x = 5
        self.bot_y = 12

        self.current_turn = TurnState.PLAYER_MOVE
        self.selected_spell = None

        # Setup Button Rectangles at the bottom area
        btn_y = self.grid_height + 15
        btn_width = 120
        btn_height = 30

        # Centering the two buttons horizontally
        spacing = 20
        start_x = (self.width - (btn_width * 2 + spacing)) // 2

        self.burn_btn_rect = pygame.Rect(start_x, btn_y, btn_width, btn_height)
        self.freeze_btn_rect = pygame.Rect(
            start_x + btn_width + spacing, btn_y, btn_width, btn_height
        )

        self.wizard = Wizard(100, 100, False)

    def draw_tile_topdown(self, surface, gx, gy, color):
        if color is None:
            return

        x = gx * self.TILE_SIZE
        y = gy * self.TILE_SIZE
        rect = pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 1)

    def get_platform_index(self, gx, gy):
        def is_platform(x, y):
            if 0 <= y < self.rows and 0 <= x < self.cols:
                return self.map[y][x] in [" ", "p", "b", "x"]
            return False

        if is_platform(gx, gy):
            return 0

        top = is_platform(gx, gy - 1)
        left = is_platform(gx - 1, gy)
        bottom = is_platform(gx, gy + 1)
        right = is_platform(gx + 1, gy)

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

    def draw_platform(self, gx, gy):
        platform_index = self.get_platform_index(gx, gy)
        x = gx * self.TILE_SIZE
        y = gy * self.TILE_SIZE

        is_dark = (gx + gy) % 2 == 0

        platform = Platform.get_platform(
            platform_index, self.TILE_SIZE, self.TILE_SIZE, is_dark=is_dark
        )
        self.screen.blit(platform, (x, y))

    def draw_ui(self):
        # Draw base background container panel
        ui_rect = pygame.Rect(
            0, self.grid_height, self.width, self.UI_PANEL_HEIGHT
        )
        pygame.draw.rect(self.screen, self.COLOR_UI_BG, ui_rect)

        # Only show buttons during spell selection phase
        if self.current_turn == TurnState.PLAYER_SPELL:
            # Burn Button styling
            burn_color = (
                self.COLOR_BTN_ACTIVE
                if self.selected_spell == SpellOption.BURN
                else self.COLOR_BTN_INACTIVE
            )
            pygame.draw.rect(self.screen, burn_color, self.burn_btn_rect)
            burn_text = self.font.render("BURN", True, (255, 255, 255))
            self.screen.blit(
                burn_text, (self.burn_btn_rect.x + 35, self.burn_btn_rect.y + 7)
            )

            # Freeze Button styling
            freeze_color = (
                self.COLOR_BTN_FREEZE
                if self.selected_spell == SpellOption.FREEZE
                else self.COLOR_BTN_INACTIVE
            )
            pygame.draw.rect(self.screen, freeze_color, self.freeze_btn_rect)
            freeze_text = self.font.render("FREEZE", True, (255, 255, 255))
            self.screen.blit(
                freeze_text,
                (self.freeze_btn_rect.x + 25, self.freeze_btn_rect.y + 7),
            )
        else:
            # Display informational text when it's not the spell state
            status_text = self.font.render(
                "Move your character to select a spell...",
                True,
                (150, 150, 150),
            )
            self.screen.blit(status_text, (20, self.grid_height + 20))

    def check_ui_clicks(self, mouse_pos):
        if self.current_turn != TurnState.PLAYER_SPELL:
            return

        if self.burn_btn_rect.collidepoint(mouse_pos):
            self.selected_spell = SpellOption.BURN

        elif self.freeze_btn_rect.collidepoint(mouse_pos):
            self.selected_spell = SpellOption.FREEZE

    def is_valid_click_area(self, mouse_pos) -> tuple[bool, int, int]:
        # Ensure the click is within the grid
        if mouse_pos[1] >= self.grid_height:
            return False, -1, -1

        gx = mouse_pos[0] // self.TILE_SIZE
        gy = mouse_pos[1] // self.TILE_SIZE

        if 0 <= gy < self.rows and 0 <= gx < self.cols:
            return True, gx, gy

        return False, -1, -1

    def execute_move(self, cur_x, cur_y, gx, gy):
        if self.current_turn == TurnState.PLAYER_MOVE:
            self.player_x = gx
            self.player_y = gy
            self.map[gy][gx] = "p"
        else:
            self.bot_x = gx
            self.bot_y = gy
            self.map[gy][gx] = "b"

        self.map[cur_y][cur_x] = "burn"
        

    def is_valid_spell_area(self, cur_x, cur_y, gx, gy):
        if self.map[gy][gx] != " ":
            return False

        dx = gx - cur_x
        dy = gy - cur_y

        is_straight = dx == 0 or dy == 0
        is_diagonal = abs(dx) == abs(dy)

        if not (is_straight or is_diagonal):
            return False

        # Check for obstructions along the path
        step_x = 0 if dx == 0 else dx // abs(dx)
        step_y = 0 if dy == 0 else dy // abs(dy)

        check_x = cur_x + step_x
        check_y = cur_y + step_y

        # Loop from player position up to (but not including) the target tile
        while (check_x, check_y) != (gx, gy):
            if self.map[check_y][check_x] != " ":
                return False

            check_x += step_x
            check_y += step_y

        return True

    # def check_freeze_spell(self):
    #     if TurnState.PLAYER_MOVE


    def handle_player_spell(self, mouse_pos):
        isValidClick, gx, gy = self.is_valid_click_area(mouse_pos)

        if not isValidClick:
            return

        if self.is_valid_spell_area(self.player_x, self.player_y, gx, gy):
            if self.selected_spell == SpellOption.BURN:
                self.map[gy][gx] = "burn"
            else:
                self.map[gy][gx] = "freeze"
                self.freeze_coords["player"]["x"] = gx
                self.freeze_coords["player"]["y"] = gy
            
            # Transition to spell phase
            self.current_turn = TurnState.PLAYER_MOVE

            self.selected_spell = None

            # Give turn to bot
            self.current_turn = TurnState.BOT_MOVE
            self.handle_turn()

    def handle_player_movement(self, mouse_pos):
        isValidClick, gx, gy = self.is_valid_click_area(mouse_pos)
        if not isValidClick:
            return

        target_tile = self.map[gy][gx]
        distance_x = abs(gx - self.player_x)
        distance_y = abs(gy - self.player_y)

        if (
            target_tile == " "
            and (distance_x <= 1 and distance_y <= 1)
            and (distance_x + distance_y > 0)
        ):

            self.execute_move(self.player_x, self.player_y, gx, gy)

            # Transition to spell phase
            self.current_turn = TurnState.PLAYER_SPELL

    def simulate_bot_move(self):
        while True:
            random_x = random.randint(-1, 1)
            random_y = random.randint(-1, 1)

            if random_y == 0 and random_x == 0:
                continue

            new_x = self.bot_x + random_x
            new_y = self.bot_y + random_y

            target_tile = self.map[new_y][new_x]

            if target_tile == " ":
                self.execute_move(self.bot_x, self.bot_y, new_x, new_y)
                return

    def simulate_bot_spell(self):
        # List of all possible grid coordinates
        possible_targets = []
        for gy in range(self.rows):
            for gx in range(self.cols):
                possible_targets.append((gx, gy))

        # Shuffle them to randomize bot choice
        random.shuffle(possible_targets)

        # Test targets until one passes valid move
        for gx, gy in possible_targets:
            if self.is_valid_spell_area(self.bot_x, self.bot_y, gx, gy):
                self.map[gy][gx] = "burn"

                return

        print("Bot has no valid spell targets.")

    def handle_turn(self, mouse_pos=None):
        if self.current_turn == TurnState.PLAYER_MOVE:
            self.handle_player_movement(mouse_pos)

        elif self.current_turn == TurnState.PLAYER_SPELL:
            if self.selected_spell == None:
                self.check_ui_clicks(mouse_pos)

            else:
                self.handle_player_spell(mouse_pos)

        elif self.current_turn == TurnState.BOT_MOVE:
            self.simulate_bot_move()

            self.current_turn = TurnState.BOT_SPELL
            self.handle_turn()

        elif self.current_turn == TurnState.BOT_SPELL:
            self.simulate_bot_spell()

            self.current_turn = TurnState.PLAYER_MOVE

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_turn(event.pos)

            # Draw Map Layout
            for gy, row in enumerate(self.map):
                for gx, tile in enumerate(row):
                    if tile != "x":
                        self.draw_platform(gx, gy)

                    if tile == "x":
                        tile_color = self.COLOR_WALL
                    elif tile == "freeze":
                        tile_color = self.COLOR_BTN_FREEZE
                    elif tile == "p":
                        tile_color = self.COLOR_PLAYER
                    elif tile == "b":
                        tile_color = self.COLOR_BOT
                    else:
                        tile_color = None

                    self.draw_tile_topdown(self.screen, gx, gy, tile_color)

            self.wizard.draw(self.screen)
            # Draw Interface Panels over map boundary
            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(60)
            self.wizard.update()


if __name__ == "__main__":
    Game().run()
