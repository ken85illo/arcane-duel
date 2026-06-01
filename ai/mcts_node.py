import math

from core.enums import MageType, Spell


class MCTSNode:
    UCB_C = 1.41  # UCB1 exploration constant (sqrt(2) ~= 1.41)

    def __init__(self, turn: MageType, action=None, parent=None):
        # Move Position, Spell and Spell Target
        self.action: tuple[tuple[int, int], Spell, tuple[int, int]] = action
        self.turn = turn
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0

    def next_turn(self):
        return MageType.PLAYER if self.turn == MageType.AI else MageType.AI

    def untried_actions(self, board):
        all_actions = self.generate_actions(board)
        tried_actions = {child.action for child in self.children}
        untried = [actions for actions in all_actions if actions not in tried_actions]

        return untried

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

            for target in targets:
                if not board.get_tile(*target).is_frozen():
                    actions.append((move, Spell.FREEZE, target))
                if move_mana >= 3:
                    actions.append((move, Spell.BURN, target))

        return actions

    def ucb1(self):
        # Force exploration of unvisited nodes
        if self.visits == 0:
            return float("inf")

        # choosing moves with higher average reward
        exploitation = self.value / self.visits

        # trying moves with less information
        exploration = self.UCB_C * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

        return exploitation + exploration

    def best_child(self):
        if self.next_turn() == MageType.AI:
            # AI chooses the best move that decreases the score of player
            return max(self.children, key=lambda child: child.ucb1())
        elif self.next_turn() == MageType.PLAYER:
            # Player chooses the best move that decreases the score of AI
            return min(self.children, key=lambda child: child.ucb1())

    def most_visited(self):
        return max(self.children, key=lambda child: child.visits)

    def _action_str(self):
        if self.action is None:
            return "Root"

        move, spell, target = self.action
        source = f"move={move}"
        spell_part = f"spell={spell.name}"
        target_part = f"target={target}" if target is not None else "target=None"

        return f"{source}, {spell_part}, {target_part}"

    def _node_label(self):
        turn_name = self.turn.name
        average_value = self.value / self.visits if self.visits else 0.0
        return (
            f"[{turn_name}] {self._action_str()} "
            f"visits={self.visits} value={self.value:.2f} avg={average_value:.2f}"
        )

    def print_tree(self, depth=0, max_depth=None):
        if max_depth is not None and depth > max_depth:
            return

        indent = "  " * depth
        print(f"{indent}{self._node_label()}")

        if max_depth is None or depth < max_depth:
            for child in self.children:
                child.print_tree(depth + 1, max_depth)
