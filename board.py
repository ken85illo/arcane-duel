import random
from tile import Tile
from enums import TileState, Mage, Spell

class Board:
    GRID_SIZE = 10
    CUMULATIVE_TILE_GEN_CHANCE = 25

    def _init_grid(self):
        # Generate the tiles with random mana
        grid = [[Tile(r, c) for c in range(self.GRID_SIZE)] for r in range(self.GRID_SIZE)]
        
        # Generate walls on the edge of the board
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if 0 == row == self.GRID_SIZE - 1 and 0 == col == self.GRID_SIZE - 1:
                    grid[row][col].state = TileState.WALL

        # Set the mana of the starting point to 0
        grid[self.player_pos[0]][self.player_pos[1]].mana = 0
        grid[self.ai_pos[0]][self.player_pos[1]].mana = 0
        
        return grid

    def _assign_random_cumulative_tiles(self):
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                target = self.grid[row][col]
                
                if random.randint(1,100) <= self.CUMULATIVE_TILE_GEN_CHANCE:
                    target.is_cumulative = True
                    target.mana = 0
                
                else:
                    target.mana = random.randint(1, 3)

    def __init__(self):
        # Place the player on top-middle of the board
        self.player_pos = (1, self.GRID_SIZE // 2)

        # Place the AI on bottom-middle of the board
        self.ai_pos = (self.GRID_SIZE - 2, self.GRID_SIZE // 2)

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

    # ===== Helper Function =====
    def get_tile(self, row, col):        
        return self.grid[row][col]

    # ===== Movement Check =====
    def is_in_bounds(self, row, col):    
        is_valid_row_move = 0 <= row < self.GRID_SIZE
        is_valid_col_move = 0 <= col < self.GRID_SIZE
    
        return is_valid_row_move and is_valid_col_move
    
    def valid_mage_moves(self, row, col):
        valid_moves = []
        
        for direction_row, direction_col in self.directions:
            new_row, new_col = row + direction_row, col + direction_col

            if self.is_in_bounds(new_row, new_col):
                target = self.get_tile(new_row, new_col)
                
                if target.is_active() and (new_row, new_col) != self.player_pos or (new_row, new_col) != self.ai_pos:
                    valid_moves.append((new_row, new_col))

        return valid_moves
    
    # ===== Spell Target Check =====
    def valid_spell_targets(self, row, col):
        valid_targets = []

        for direction_row, direction_col in self.directions:
            new_row, new_col = row + direction_row, col + direction_col

            # Loop into a straight line until it reaches the bounds whch will result in queen-like target
            while self.is_in_bounds(new_row, new_col):
                target = self.get_tile(new_row,new_col)

                # Break the target line if its obstructed by player or AI 
                if (new_row, new_col) == self.player_pos or (new_row, new_col) == self.ai_pos:
                    break

                # Break the target line at empty tile
                if target.state == TileState.EMPTY or target.state == TileState.WALL:
                    break
                
                # Break the target line at frozen tile but make it targetable (can be burned)
                if target.state == TileState.FROZEN:
                    valid_targets.append((new_row, new_col))
                    break

                valid_targets.append((new_row, new_col))
                new_row += direction_row
                new_col += direction_col

        return valid_targets
    
    # ===== Apply Actions =====
    def apply_move(self, who: Mage, row, col):
        # Move player or AI 
        if who == Mage.PLAYER:
            old_row, old_col = self.player_pos
            self.player_mana += self.get_tile(row, col).mana
            self.player_pos = (row, col)

        elif who == Mage.AI:
            old_row, old_col = self.ai_pos
            self.ai_mana += self.get_tile(row, col).mana
            self.ai_pos = (row, col)

        # Destroy the old tile
        self.get_tile(old_row, old_col).destroy_tile()
        
    def can_afford_burn(self, who: Mage):
        return (self.player_mana if who == Mage.PLAYER else self.ai_mana) >= 3

    def apply_spell(self, who: Mage, spell, row, col):
        target = self.get_tile(row, col)
        
        if spell == Spell.FREEZE:
            if target.is_frozen():
                return
            
            target.freeze_tile()
        
        elif spell == Spell.BURN:
            if not self.can_afford_burn(who):
                return

            if target.state == TileState.FROZEN:
                target.unfreeze_tile()

                if who == Mage.PLAYER:
                    self.player_mana -= 3
                    self.player_mana += 1 # Bonus +1 for breaking ice of frozen tile

                elif who == Mage.AI:
                    self.ai_mana -= 3
                    self.ai_mana += 1 # Bonus +1 for breaking ice of frozen tile

        else:
            target.destroy_tile()

            if who == Mage.PLAYER:
                self.player_mana -= 3

            elif who == Mage.AI:
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
    

    
                                

        





        
        
        
    