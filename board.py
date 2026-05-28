from collections import deque
import random
from tile import Tile
from enums import Direction, TileState, Spell, MageType
from ui_util import GridConfig
from mage import MageStates
from bfs_board import breadth_first_search

class Board:
    CUMULATIVE_TILE_GEN_CHANCE = 25

    def _init_grid(self):
        # Generate the tiles with random mana
        grid = [[Tile(r, c) for c in range(GridConfig.GRID_SIZE)] for r in range(GridConfig.GRID_SIZE)]
        
        # Generate walls on the edge of the board
        for row in range(GridConfig.GRID_SIZE):
            for col in range(GridConfig.GRID_SIZE):
                if row == 0 or row == GridConfig.GRID_SIZE - 1 or col == 0 or col == GridConfig.GRID_SIZE - 1:
                    grid[row][col].state = TileState.WALL

        # Set the mana of the starting points to 0
        grid[self.player_pos[0]][self.player_pos[1]].mana = 0
        grid[self.ai_pos[0]][self.ai_pos[1]].mana = 0
        
        return grid

    def _assign_random_cumulative_tiles(self):
        for row in range(GridConfig.GRID_SIZE):
            for col in range(GridConfig.GRID_SIZE):
                target = self.grid[row][col]
                
                if random.randint(1,100) <= self.CUMULATIVE_TILE_GEN_CHANCE:
                    target.is_cumulative = True
                    target.mana = 0
                
                else:
                    target.mana = random.randint(1, 3)

    def __init__(self, player_sprite, ai_sprite):


        # Place the player on top-middle of the board
        self.player_pos = (1, GridConfig.GRID_SIZE // 2)

        # Place the AI on bottom-middle of the board
        self.ai_pos = (GridConfig.GRID_SIZE - 2, GridConfig.GRID_SIZE // 2)

        # Initialize the grid and mage positions
        self.grid = self._init_grid()
        
        # Randomize cumulative tile positions
        self._assign_random_cumulative_tiles()
        
        # Set both mages a 0 starting mana
        self.player_mana = 0
        self.ai_mana = 0

        # Valid mage and spell directions
        self.directions = [
            (0, 1), # Right
            (0, -1), # Left
            (1, 0), # Down
            (-1, 0), # Up
            (1, 1), # Bottom-Right
            (1, -1), # Bottom-Left
            (-1, 1), # Upper-Right
            (-1, -1), # Upper-Left
        ]

        self.player_direction = Direction.RIGHT
        self.ai_direction = Direction.RIGHT

        self.player_sprite = player_sprite
        self.ai_sprite = ai_sprite

    # ===== Helper Function =====
    def get_tile(self, row, col):        
        return self.grid[row][col]

    # ===== Movement Check =====
    def is_in_bounds(self, row, col):    
        is_valid_row_move = 0 <= row < GridConfig.GRID_SIZE
        is_valid_col_move = 0 <= col < GridConfig.GRID_SIZE
    
        return is_valid_row_move and is_valid_col_move
    
    def valid_mage_moves(self, row, col):
        valid_moves = []
        
        for direction_row, direction_col in self.directions:
            new_row, new_col = row + direction_row, col + direction_col

            if self.is_in_bounds(new_row, new_col):
                target = self.get_tile(new_row, new_col)
                
                # only allow active tiles that are not occupied by either mage
                if target.is_active() and (new_row, new_col) != self.player_pos and (new_row, new_col) != self.ai_pos:
                    valid_moves.append((new_row, new_col))

        return valid_moves
    
    # ===== Spell Target Check =====
    def valid_spell_targets(self, row, col):
        valid_targets = []

        for direction_row, direction_col in self.directions:
            new_row, new_col = row + direction_row, col + direction_col

            # Loop into a straight line until it reaches the bounds whch will result in queen-like target
            while self.is_in_bounds(new_row, new_col):
                target = self.get_tile(new_row, new_col)

                # # Break the target line if its obstructed by player or AI 
                if (new_row, new_col) == self.player_pos or (new_row, new_col) == self.ai_pos:
                    break

                if target.state == TileState.WALL:
                    break

                # Break the target line at empty tile
                if target.state == TileState.EMPTY:
                    new_row += direction_row
                    new_col += direction_col
                    continue
                
                # Break the target line at frozen tile but make it targetable (can be burned)
                if target.state == TileState.FROZEN:
                    valid_targets.append((new_row, new_col))
                    break

                valid_targets.append((new_row, new_col))
                new_row += direction_row
                new_col += direction_col

        return valid_targets
    
    # ===== Apply Actions =====
    def apply_move(self, who: MageType, row, col):
        # Move player or AI 
        if who == MageType.PLAYER:
            old_row, old_col = self.player_pos
            self.player_mana += self.get_tile(row, col).mana
            self.player_pos = (row, col)

            if self.player_sprite:
                if row < old_row and col == old_col:
                    self.player_sprite.set_state(MageStates.BACK_WALK)
                elif row > old_row and col == old_col:
                    self.player_sprite.set_state(MageStates.FRONT_WALK)
                else:
                    self.player_sprite.set_state(MageStates.SIDE_WALK)

            if old_col != col:
                self.player_direction  = Direction.LEFT if col < old_col else Direction.RIGHT

        elif who == MageType.AI:
            old_row, old_col = self.ai_pos
            self.ai_mana += self.get_tile(row, col).mana
            self.ai_pos = (row, col)

            if self.ai_sprite:
                if row < old_row and col == old_col:
                    self.ai_sprite.set_state(MageStates.BACK_WALK)
                elif row > old_row and col == old_col:
                    self.ai_sprite.set_state(MageStates.FRONT_WALK)
                else:
                    self.ai_sprite.set_state(MageStates.SIDE_WALK)

            if old_col != col:
                self.ai_direction  = Direction.LEFT if col < old_col else Direction.RIGHT

        # Destroy the old tile
        self.get_tile(old_row, old_col).destroy_tile()
        
    def can_afford_burn(self, who: MageType):
        return (self.player_mana if who == MageType.PLAYER else self.ai_mana) >= 3

    def apply_spell(self, who: MageType,  spell: Spell, row, col):
        target = self.get_tile(row, col)
        print(f"{who.name} casts {spell.name} on tile ({row}, {col}) with state {target.state.name} and mana {target.mana}")

        # Play animation for attack
        if who == MageType.PLAYER:
            self.player_sprite.set_state(MageStates.ATTACK)
            _, old_col  = self.player_pos 

            if old_col != col:
                self.player_direction = Direction.LEFT if col < old_col else Direction.RIGHT 
        else:
            self.ai_sprite.set_state(MageStates.ATTACK)
            _, old_col  = self.ai_pos 

            if old_col != col:
                self.ai_direction = Direction.LEFT if col < old_col else Direction.RIGHT 

        if spell == Spell.FREEZE:
            if target.is_frozen():
                return
            
            target.freeze_tile()
        
        elif spell == Spell.BURN:
            if not self.can_afford_burn(who):
                return

            if target.state == TileState.FROZEN:
                target.unfreeze_tile()

                if who == MageType.PLAYER:
                    self.player_mana -= 3
                    self.player_mana += target.mana # Bonus +1 for breaking ice of frozen tile

                elif who == MageType.AI:
                    self.ai_mana -= 3
                    self.ai_mana += target.mana # Bonus +1 for breaking ice of frozen tile

            else:
                target.destroy_tile()

                if who == MageType.PLAYER:
                    self.player_mana -= 3

                elif who == MageType.AI:
                    self.ai_mana -= 3
            
    # ===== Per-turn changes ====
    
    def turn_decrement_freeze_timer(self):
        # Increment the timer of the freezed tile
        for row in self.grid:
            for tile in row:
                tile.freeze_decrement()
    
    def turn_increase_cumulative_mana(self):
        for row in self.grid:
            for tile in row:
                # Chance to increase mana of cumulative mana tile
                tile.cumulate_mana()
    
    # ===== Create Board Copy for MCTS =====
    def create_board_copy(self):
        board_copy = Board.__new__(Board)  # Create a new instance without calling __init__
        board_copy.grid = [
            [self.get_tile(row, col).copy() for col in range(GridConfig.GRID_SIZE)] for row in range(GridConfig.GRID_SIZE)
        ]
        board_copy.player_pos = self.player_pos
        board_copy.ai_pos = self.ai_pos
        board_copy.player_mana = self.player_mana
        board_copy.ai_mana = self.ai_mana
        board_copy.directions = self.directions.copy()
        board_copy.player_sprite = None
        board_copy.ai_sprite = None

        return board_copy
    
    
    def victory_lap(self, who: MageType):
        pos = self.player_pos if who == MageType.PLAYER else self.ai_pos
        enemy_pos = self.ai_pos if who == MageType.PLAYER else self.player_pos

        reachable_mana = breadth_first_search(self, pos, enemy_pos)
        
        if who == MageType.PLAYER:
            self.player_sprite.set_state(MageStates.WIN)
            self.ai_sprite.set_state(MageStates.DEATH)
            self.player_mana += reachable_mana
        else:
            self.ai_sprite.set_state(MageStates.WIN)
            self.player_sprite.set_state(MageStates.DEATH)
            self.ai_mana += reachable_mana
    
                                

        





        
        
        
    
