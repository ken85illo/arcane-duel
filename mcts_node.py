import math
from enums import MageType, Spell 

class MCTSNode:   
    UCB_C = 1.41  # UCB1 exploration constant (sqrt(2) ~= 1.41)

    def __init__(self, turn: MageType,  action = None, parent = None):
        # Move Position, Spell and Spell Target
        self.action: tuple[tuple[int, int], Spell, tuple[int, int]]= action
        self.turn = turn
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0


    def next_turn(self):
        return MageType.PLAYER if self.turn == MageType.AI else MageType.AI

    def generate_actions(self, board):
        actions = []

        if self.next_turn() == MageType.AI:
            position = board.ai_pos
            current_mana = board.ai_mana
        else:
            position = board.player_pos
            current_mana = board.player_mana

        moves = board.valid_mage_moves(*position)

        for move in moves:
            targets = board.valid_spell_targets(*move)
            move_mana = current_mana + board.get_tile(*move).mana

            # Add a move-only action even if there are no valid spell targets.
            actions.append((move, Spell.FREEZE, None))

            for target in targets:
                actions.append((move, Spell.FREEZE, target))
                if move_mana >= 3:
                    actions.append((move, Spell.BURN, target))


        return actions
        
        
    def ucb1(self):
        if self.visits == 0:
            return float('inf')

        return (self.value / self.visits) + self.UCB_C * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self):
        return max(self.children, key=lambda child: child.ucb1())

    def most_visited(self):
        return max(self.children, key = lambda child: child.visits)
            

    
