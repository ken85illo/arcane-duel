# Arcane Duel
Arcane Duel is a grid strategy game for two players. It's inspired by the classic move and delete gameplay of Isola but adds a twist by allowing players to choose between permanently destroying tiles or by temporarily blocking them. The mages settled their duels in the Floating Isles with each isle pulsing with mana, raw magical energy drawn from the land itself, and it is this power that both fuels the duel and slowly destroys the arena.

## Features

- The playing board can be a 5x5, 7x7 or 9x9 grid with walls, burnable tiles, regular tiles (1 to 3 mana), cumulative tiles (0 to 5 mana), and frozen/empty states
- AI opponent powered by Monte Carlo Tree Search (MCTS)
- Victory lap portion collected by Breadth-First Search (BFS)

## Gameplay

1. Start a new game from the main menu.
2. Each turn consists of two phases:
   - Move your mage to an adjacent active tile.
   - Cast a spell from your new position.
3. Collect mana by moving onto mana tiles.
4. Use `Freeze` to immobilize tiles and `Burn` to destroy tiles or break frozen ones.
5. The AI alternates turns with the player.
6. The game stops when the Player or AI can no longer move to an adjacent tile.
7. The winner is determined by who has the most mana after the victory lap.

## Controls

- `Left click` – Select and confirm moves/spell targets
- `Escape` – Return to main menu
- `R` – Restart after game over

## Requirements

- Python 3.8+
- pygame

## Installation

1. Create a Python virtual environment:
```cmd
python -m venv venv
```

2. Activate the virtual environment
```cmd
.venv\Scripts\activate.bat
```

3. Install dependencies:

```powershell
python -m pip install pygame-ce
```

## Running the Game

From the project root:

```powershell
python main.py
```

## Project Structure

- `game.py` – Main game loop and phase logic
- `board.py` – Board state, movement, and spell application
- `mage.py` – Mage animation and sprite handling
- `mcts.py` – AI decision-making logic
- `board_display.py`, `panel_display.py`, `flash_display.py`, `game_over_display.py`, `main_menu_display.py` – Game UI rendering
- `assets/` – Sprite sheets and image resources

## Notes

- The AI uses Monte Carlo Tree Search for planning moves and spells.
- Tile mana is randomized each game for replayability.
- The project is designed for local play and does not require online connectivity.
