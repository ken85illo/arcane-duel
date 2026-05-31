import random
import time
from ai.bfs import breadth_first_search
from ai.mcts_node import MCTSNode
from core.enums import Spell, MageType

class MCTS:
    def __init__(self, max_iterations=5000):
        self.max_iterations = max_iterations

    def print_search_tree(self, node, depth=0):
        if node is None:
            return

        indent = "│   " * depth

        action_str = "ROOT"
        if node.action:
            move, spell, target = node.action
            action_str = f"Move={move} Spell={spell.name} Target={target}"

        avg_value = node.value / node.visits if node.visits > 0 else 0

        print(
            f"{indent}├── {action_str} "
            f"[Visits={node.visits}, "
            f"Value={node.value:.2f}, "
            f"Avg={avg_value:.2f}]"
        )

        children = sorted(
            node.children,
            key=lambda c: c.visits,
            reverse=True
        )

        for child in children:
            self.print_search_tree(child, depth + 1)

    def mcts_best_action(self, board):
        print(f"Max Iterations: {self.max_iterations}")
        root = MCTSNode(turn=MageType.PLAYER)
        
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

        print("\n=== MCTS SEARCH TREE ===")
        self.print_search_tree(root)
        print("========================\n")
        
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
            node = node.best_child()
            self.apply_action(board, node.turn, node.action)

        return node, board
    
    # 2. Expansion: try one new action
    def _expansion(self, node, board):
        untried =  node.untried_actions(board)
        
        if untried:
            action = random.choice(untried)
            next_turn = node.next_turn() 

            child = MCTSNode(next_turn, action=action, parent=node)
            node.children.append(child)

            self.apply_action(board, next_turn, action)
            node = child

        return node, board

    # Rollout plays random moves which will be used for simulation
    def _rollout(self, current_turn, board):
        while True:  
            temp_node = MCTSNode(turn=current_turn)
            actions = temp_node.generate_actions(board)

            if not actions:
                break

            next_turn = temp_node.next_turn()
            action = random.choice(actions)
            self.apply_action(board, next_turn, action)
            current_turn = next_turn
        
        return board
        
    # 3. Simulation: score the simulated board
    def _simulation(self, starting_turn, board):
        board = self._rollout(starting_turn, board)

        ai_reachable_tiles, ai_reachable_mana, player_reachable_tiles, player_reachable_mana = self._bfs_both(board)
        mana_score = (board.ai_mana + ai_reachable_mana) - (board.player_mana + player_reachable_mana)
        territory_score  = (ai_reachable_tiles - player_reachable_tiles) * 1.5
        player_moves = len(board.valid_mage_moves(*board.player_pos))
        isolation_bonus = max(0, 4 - player_moves) * 3.0

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

        position =  board.ai_pos if turn == MageType.AI else board.player_pos
        valid_targets = board.valid_spell_targets(*position)

        if target is not None and target not in valid_targets:
            if valid_targets:
                target = random.choice(valid_targets)
            else:
                target = None

        if target:
            if spell == Spell.BURN and not board.can_afford_burn(turn):
                return

            tile = board.get_tile(*target)
            if spell == Spell.FREEZE:
                if tile.is_frozen():
                    return

                tile.freeze_tile()
            elif spell == Spell.BURN:
                tile.destroy_tile()
        
        board.turn_decrement_freeze_timer()
        board.turn_increase_cumulative_mana()

    def _bfs_both(self, board): 
        ai_reachable_tiles, ai_reachable_mana, _ = breadth_first_search(board, board.ai_pos, board.player_pos)
        player_reachable_tiles, player_reachable_mana, _ = breadth_first_search(board, board.player_pos, board.ai_pos)
        
        return ai_reachable_tiles, ai_reachable_mana, player_reachable_tiles, player_reachable_mana

