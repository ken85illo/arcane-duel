import random
from bfs_board import breadth_first_search
from mcts_node import MCTSNode
from enums import Spell, MageType, Spell
from collections import deque

class MCTS:
    def __init__(self, max_iterations=1000):
        self.max_iterations = max_iterations

        
    def _selection(self, node, board):
        while node.children and not node.untried_actions(board):
            node = node.best_child()
            self._rollout(board, node.action)

        return node
    
    def _expansion(self, node, board):
        untried =  node.untried_actions(board)
        
        if untried:
            action = untried.pop(random.randrange(len(untried)))
            self._rollout(board, action)
            child = MCTSNode(action=action, parent=node)
            node.children.append(child)
            node = child

        return node
        
    def _simulation(self, board):
        ai_reachable_tiles, ai_reachable_mana, player_reachable_tiles, player_reachable_mana = self._bfs_both(board)
        mana_score = (board.ai_mana + ai_reachable_mana) - (board.player_mana + player_reachable_mana)
        territory_score  = (ai_reachable_tiles - player_reachable_tiles) * 1.5
        player_moves = len(board.valid_mage_moves(*board.player_pos))
        isolation_bonus = max(0, 4 - player_moves) * 3.0

        return mana_score + territory_score + isolation_bonus
    
    def _backpropagation(self, node, score):
        while node:
            node.visits += 1
            node.value += score
            node = node.parent

    def _rollout(self, board, action: tuple[tuple[int, int], Spell, tuple[int, int]]):
        move, spell, target = action
        
        board.apply_move(MageType.AI, *move)    
        valid_targets = board.valid_spell_targets(*board.ai_pos)
        target = target if target in valid_targets else (random.choice(valid_targets) if valid_targets else None)

        if target:
            tile = board.get_tile(*move)
            if spell == Spell.FREEZE:
                if not tile.is_frozen():
                    tile.freeze_tile()
            elif spell == Spell.BURN:
                tile.destroy_tile()
    
    def _bfs_both(self, board): 
        ai_target, ai_mana = breadth_first_search(board, board.ai_pos, board.player_pos)
        player_target, player_mana = breadth_first_search(board, board.player_pos, board.ai_pos)
        
        return ai_target, ai_mana, player_target, player_mana

    def mcts_best_action(self, board):
        root = MCTSNode()
        
        for _ in range(self.max_iterations):
            node = root
            board_sim = board.create_board_copy()

            # Selection
            node = self._selection(node, board_sim)

            # Expansion
            node = self._expansion(node, board_sim)

            # Simulation
            score = self._simulation(board_sim)

            # Backpropagation
            self._backpropagation(node, score)

        if not root.children:
            # Pick a random valid action of MCTS Found nothing
            moves = board.valid_mage_moves(*board.ai_pos)
            targets = board.valid_spell_targets(*board.ai_pos)

            if moves and targets:
                return (random.choice(moves), Spell.FREEZE, random.choice(targets))

            return None
        
        return root.most_visited().action

            



