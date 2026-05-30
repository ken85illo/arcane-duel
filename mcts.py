import random
from bfs_board import breadth_first_search
from mcts_node import MCTSNode
from enums import Spell, MageType

class MCTS:
    def __init__(self, max_iterations=1000):
        self.max_iterations = max_iterations

    def mcts_best_action(self, board):
        root = MCTSNode(turn=MageType.AI)
        
        for i in range(self.max_iterations):
            node = root
            board_sim = board.create_board_copy()

            # Selection
            node, board_sim = self._selection(node, board_sim)

            # Expansion
            node, board_sim = self._expansion(node, board_sim)

            # Evaluation
            score = self._simulation(node.turn, board_sim)

            # Backpropagation
            self._backpropagation(node, score)

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
        while node.children and not node.untried_actions(board):
            best_child = node.best_child()
            self.apply_action(board, node.turn, best_child.action)
            node = best_child

        return node, board
    
    # 2. Expansion: try one new action
    def _expansion(self, node, board):
        untried = node.untried_actions(board)
        
        if untried:
            action = random.choice(untried)
            next_turn = node.next_turn()

            child = MCTSNode(next_turn, action=action, parent=node)
            node.children.append(child)

            self.apply_action(board, node.turn, action)
            node = child

        return node, board

    # 3. Simulation: score the simulated board
    def _simulation(self, starting_turn, board):
        return self._evaluate_board(board)

    def _evaluate_board(self, board):
        ai_reachable_tiles, ai_reachable_mana, _ = breadth_first_search(board, board.ai_pos, board.player_pos)
        player_reachable_tiles, player_reachable_mana, _ = breadth_first_search(board, board.player_pos, board.ai_pos)

        mana_score = (board.ai_mana + ai_reachable_mana) - (board.player_mana + player_reachable_mana)
        territory_score = (ai_reachable_tiles - player_reachable_tiles) * 1.5
        player_moves = len(board.valid_mage_moves(*board.player_pos))
        isolation_bonus = max(0, 4 - player_moves) * 3

        return mana_score + territory_score + isolation_bonus
    
    # 4. Backpropagation: update all ancestors
    def _backpropagation(self, node, score):
        while node:
            node.visits += 1
            node.value += score
            node = node.parent


    def apply_action(self, board, turn:MageType, action: tuple[tuple[int, int], Spell, tuple[int, int]]):
        move, spell, target = action

        board.apply_move(turn, *move)

        position = board.ai_pos if turn == MageType.AI else board.player_pos
        valid_targets = board.valid_spell_targets(*position)

        if target is not None and target not in valid_targets:
            if valid_targets:
                target = random.choice(valid_targets)
            else:
                target = None

        if target:
            board.apply_spell(turn, spell, *target)

        board.turn_decrement_freeze_timer()
        board.turn_increase_cumulative_mana()


