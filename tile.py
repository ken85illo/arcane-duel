import random
from enums import TileState

class Tile:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.state = TileState.ACTIVE  # All tiles start as active
        self.mana = 0
        self.is_cumulative = False  # If True, tile slowly gains mana each round
        self.freeze_timer = 0 # Rounds remaining while frozen
    
    # ===== Tile Check Helpers =====
    def is_active(self):
        # Check if player or AI can pass throught this tile
        # or it can be targeted by spell
        return self.state == TileState.ACTIVE

    def is_frozen(self):
        return self.state == TileState.FROZEN

    # ===== State Changes ====
    def destroy_tile(self):
        self.state = TileState.EMPTY   
    
    def freeze_tile(self):
        self.state = TileState.FROZEN

    def unfreeze_tile(self):
        self.state = TileState.ACTIVE
        self.freeze_timer = 0

    # Freeze Countdown
    def freeze_decrement(self):
        if self.state == TileState.FROZEN:
            self.freeze_timer -= 1

            # Check if frozen tile should be unfrozen
            if self.freeze_decrement <= 0:
                self.state = TileState.ACTIVE
                self.freeze_timer = 0
    
    # Cumulative Mana Tile Chance Increase
    def cumulate_mana(self):
        # Runs if the tile is cumulative, active, and the mana is under 5 (max)
        if self.is_cumulative and self.state == TileState.ACTIVE and self.mana < 5:
            
            # 15% Chance of increasing by 1 mana value
            if random.randint(1, 100) <= 15: 
                self.mana += 1