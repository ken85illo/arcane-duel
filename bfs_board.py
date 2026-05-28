from collections import deque

def breadth_first_search(board, start: tuple[int, int], enemy_pos: tuple[int, int]):
    visited = set([start])
    queue = deque([start])
    reachable_mana = 0

    while queue:
        row, col = queue.popleft()

        for direction_row, direction_col in board.directions:
            new_row, new_col = row + direction_row, col + direction_col

            if (new_row, new_col) in visited:
                continue

            if board.is_in_bounds(new_row, new_col):
                tile = board.get_tile(new_row, new_col)

                if tile.is_active() and (new_row, new_col) != enemy_pos:
                    visited.add((new_row, new_col))
                    reachable_mana += tile.mana
                    queue.append((new_row, new_col))
        
    return reachable_mana
