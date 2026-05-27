import math
from enums import Spell 

class MCTSNode:   
    UCB_C = math.sqrt(2)  # UCB1 exploration constant (sqrt(2) ~= 1.41)

    def __init__(self, action = None, parent = None):
        # Move Position, Spell and Spell Target
        self.action: tuple[tuple[int, int], Spell, tuple[int, int]]= action
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0
        self._untried = None

    def untried_actions(self, board):
        if self._untried is None:
            self._untried = self._generate_actions(board)
    
        return self._untried

    def _generate_actions(self, board):
        moves = board.valid_mage_moves(*board.ai_pos)
        targets = board.valid_spell_targets(*board.ai_pos)

        freeze = [
            (move, Spell.FREEZE, target) for move in moves for target in targets 
        ]
        burn  = [
            (move, Spell.BURN, target) for move in moves for target in targets
        ]

        return freeze + burn
        
        
    def ucb1(self):
        if self.visits == 0:
            return float('inf')

        return (self.value / self.visits) + self.UCB_C * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self):
        return max(self.children, key=lambda child: child.ucb1())

    def most_visited(self):
        return max(self.children, key = lambda child: child.visits)
            

    