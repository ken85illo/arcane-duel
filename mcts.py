import random
import time
from bfs_board import breadth_first_search
from mcts_node import MCTSNode
from enums import Spell, MageType, Spell
from collections import deque

class MCTS:
    def __init__(self, simulation_depth = 6, max_iterations=3000):
        self.max_iterations = max_iterations
        self.simulation_depth = simulation_depth

    def mcts_best_action(self, board):
        root = MCTSNode(turn=MageType.PLAYER, board=board)
        
        for i in range(self.max_iterations):
            node = root
            board_sim = board.create_board_copy()

            # Selection
            node, board_sim = self._selection(node, board_sim)

            # Expansion
            node, board_sim = self._expansion(node, board_sim)

            # Simulation
            score = self._simulation(node.turn, board_sim)

            # Backpropagation
            self._backpropagation(node, score)

            time.sleep(0.001)

        if not root.children:
            moves = board.valid_mage_moves(*board.ai_pos)
            if not moves:
                return None

            move = random.choice(moves)
            targets = board.valid_spell_targets(*move)
            target = random.choice(targets) if targets else None

            if target is not None and board.ai_mana + board.get_tile(*move).mana >= 3:
                return (move, Spell.BURN, target)

            return (move, Spell.FREEZE, target)
        
        return root.most_visited().action


    # 1. Selection: descend to a node with unexplored actions
    def _selection(self, node, board):
        while node.children and not self._untried_actions(node, board):
            node = node.best_child()
            self._apply_move(board, node.turn, node.action)

        return node, board
    

    # 2. Expansion: try one new action
    def _expansion(self, node, board):
        untried =  self._untried_actions(node, board)
        
        if untried:
            action = random.choice(untried)
            next_turn = node.next_turn()

            self._apply_move(board, next_turn, action)

            child = MCTSNode(next_turn, board=board, action=action, parent=node)
            node.children.append(child)
            node = child

        return node, board

    # Rollout plays random moves which will be used for simulation
    def _rollout(self, current_turn, board):
        for _ in range(self.simulation_depth):  
            temp_node = MCTSNode(turn=current_turn, board=board)
            actions = temp_node.generate_actions(board)

            if not actions:
                break

            action = random.choice(actions)
            next_turn = temp_node.next_turn()
            self._apply_move(board, next_turn, action)
            current_turn =  next_turn
        
        return board

        
    # 3. Simulation: score the simulated board
    def _simulation(self, starting_turn, board):
        board = self._rollout(starting_turn, board)
            
        ai_reachable_mana,  player_reachable_mana = self._bfs_both(board)
        mana_score = (board.ai_mana + ai_reachable_mana) - (board.player_mana + player_reachable_mana)
        return mana_score 
    
    # 4. Backpropagation: update all ancestors
    def _backpropagation(self, node, score):
        while node:
            node.visits += 1
            node.value += score
            node = node.parent

    def _untried_actions(self, node, board):
        all_actions = node.generate_actions(board)
        tried_actions = {child.action for child in node.children}
        untried = [actions for actions in all_actions if actions not in tried_actions]

        return untried

    def _apply_move(self, board, turn:MageType, action: tuple[tuple[int, int], Spell, tuple[int, int]]):
        move, spell, target = action

        board.apply_move(turn, *move)

        position =  board.ai_pos if turn == MageType.AI else board.player_pos
        valid_targets = board.valid_spell_targets(*position)

        if target is not None and target not in valid_targets:
            if valid_targets:
                target = random.choice(valid_targets),
            else:
                target = None

        if target:
            if spell == Spell.BURN and not board.can_afford_burn(turn):
                return

            tile = board.get_tile(*target)
            if spell == Spell.FREEZE:
                if not tile.is_frozen():
                    tile.freeze_tile()
            elif spell == Spell.BURN:
                tile.destroy_tile()

    def _bfs_both(self, board): 
        ai_reachable_mana = breadth_first_search(board, board.ai_pos, board.player_pos)
        player_reachable_mana = breadth_first_search(board, board.player_pos, board.ai_pos)
        
        return ai_reachable_mana, player_reachable_mana

