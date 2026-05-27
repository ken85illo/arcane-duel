import random
import sys

from mcts import MCTS
from enums import Phase, TileState, AIState, Winner
from board import Board
from board_display import BoardDisplay, tile_rect
from mage import Mage, MageStates
from board import Board
from enums import MageType, Spell

from ui_util import GridConfig
from panel_display import PanelDisplay
import pygame

class Game:
    PANEL_WIDTH = 400
    SCREEN_WIDTH = GridConfig.GRID_SIZE * GridConfig.TILE_SIZE + PANEL_WIDTH
    SCREEN_HEIGHT = GridConfig.GRID_SIZE * GridConfig.TILE_SIZE
    
    def _make_font(self, size, bold=False):
        for name in ("dejavusans", "liberationsans", "freesans", "droidsans"):
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f:
                    return f
            except Exception:
                pass
        return pygame.font.Font(None, size + 6)  # Fall back to pygame's built-in bitmap font

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Arcane Duel")
        self.screen = pygame.display.set_mode (
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Font sizes for different UI elements
        self.font_xl = self._make_font(38, True)  # Scores, game-over text
        self.font_lg = self._make_font(22, True)  # Header title
        self.font_md = self._make_font(16)             # Spell buttons, mana numbers
        self.font_sm = self._make_font(13)             # Legend, combat log, labels

        self.clock = pygame.time.Clock()
        self._new_game()
    
    # ===== Game Setup =====
    def _new_game(self):
        self.player = Mage(False)
        self.ai = Mage(True)
        self.phase =  Phase.PLAYER_MOVE # self._randomize_starting_turn() # Starting turn
        self.board = Board(self.player, self.ai) # Starting board
        self.board_display = BoardDisplay(self)
        self.panel_display = PanelDisplay(self)
        self.hover_tile   = None # Grid position under the mouse cursor
        self.valid_player_move_set = set() # Valid movement targets for the player this turn
        self.valid_player_spell_set = set() # Valid spell targets for the player this turn
        self.spell_choice = Spell.FREEZE
        self.winner = None     
        # == To Be Added
        # self.log = [] # Combat log entries (max 9 lines)
        # self.flash_msg    = ""             # Short message shown in the center of the board
        # self.flash_timer  = 0             # How many frames the flash message remains visible
        
        self.ai_busy = False
        self.ai_delay = 0
        self.ai_stage = AIState.THINKING
        self.ai_action  = None
        self.mcts = MCTS()

        self.update_valid_moves()

    def _randomize_starting_turn(self) -> Phase:
        r = random.randint(1, 100)

        return Phase.PLAYER_MOVE if r <= 50 else Phase.AI_MOVE

    # State helpers section

    def update_valid_moves(self):
        row, col = self.board.player_pos
        self.valid_player_move_set = self.board.valid_mage_moves(row, col)

    def update_valid_spells(self):
        row, col = self.board.player_pos
        self.valid_player_spell_set = self.board.valid_spell_targets(row, col)

    # ===== Action Listeners =====
    def _tile_at(self, px, py):
        # px, py reflects mouse position
        for row in range(GridConfig.GRID_SIZE):
            for col in range(GridConfig.GRID_SIZE):
                if tile_rect(row, col).collidepoint(px, py):
                    return row, col

        return None

    def _events(self):
        mx, my = pygame.mouse.get_pos()

        # Tracks tile currently hovered at (future use: highlight tile selection) 
        self.hover_tile = self._tile_at(mx, my)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    
            
            # When Game Over, restarts on 'R' key press
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.phase == Phase.GAME_OVER:
                self._new_game()
            
            # Handles left mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.phase == Phase.PLAYER_MOVE:  
                    self._handle_player_click(mx, my)

                if self.phase == Phase.PLAYER_SPELL:
                    self._handle_player_click(mx, my)
    
    def _handle_player_click(self, mx, my):
        clicked_tile = self._tile_at(mx, my)

        if self.phase == Phase.PLAYER_MOVE:
            if clicked_tile and clicked_tile in self.valid_player_move_set:
                row, col = clicked_tile
                self.board.apply_move(MageType.PLAYER, row, col)
                self.update_valid_spells()
                self.phase = Phase.PLAYER_SPELL # Transition to spell phase after a move
                self.spell_choice = None
            else:
                return # Invalid move, do nothing
        
        elif self.phase == Phase.PLAYER_SPELL:
            freeze_btn, burn_btn = self.panel_display._btn_rects()

            # Clicked the FREEZE button
            if freeze_btn.collidepoint(mx, my):
                self.spell_choice = Spell.FREEZE
                return

            # Clicked the BURN button
            if burn_btn.collidepoint(mx, my):
                if not self.board.can_afford_burn(MageType.PLAYER):
                    return
                
                self.spell_choice = Spell.BURN
                return

            # Click a tile after selecting a spell
            if clicked_tile:

                if not self.spell_choice:
                    return # No spell selected, do nothing

                if clicked_tile not in self.valid_player_spell_set:
                    return # Invalid spell target, do nothing
                    
                row, col = clicked_tile

                if self.board.get_tile(row, col).is_frozen() and self.spell_choice == Spell.FREEZE:
                    return # Can't freeze a tile that's already frozen, do nothing

                if self.spell_choice == Spell.BURN and not self.board.can_afford_burn(MageType.PLAYER):
                    self.spell_choice = None # Reset spell choice since burn can't be cast
                    return # DOUBLE CHECK. Can't afford burn, do nothing

                
                self.board.apply_spell(MageType.PLAYER, self.spell_choice, row, col)
                self._end_player_turn()
        
        else:
            return # Not player's turn, do nothing

    def _end_player_turn(self):
        self.board.turn_increase_cumulative_mana()
        self.board.turn_decrement_freeze_timer()

        # Check if AI is trapped
        if not self.board.valid_mage_moves(*self.board.ai_pos):
            self.board.victory_lap()
            self._finish()
            return

        # Start the AI's turn
        self.phase = Phase.AI_MOVE
        self.ai_busy   = True
        self.ai_stage  = AIState.THINKING
        self.ai_delay  = 0
        self.ai_action = None
    
    def _finish(self):
        player_mana, ai_mana = self.board.player_mana, self.board.ai_mana
        self.winner = Winner.PLAYER if player_mana > ai_mana else (Winner.AI if ai_mana > player_mana else Winner.DRAW)
        self.phase = Phase.GAME_OVER
    
    # ===== AI Logic =====

    DELAY_THINK  = 45
    DELAY_MOVE   = 40
    DELAY_SPELL  = 50
    DELAY_FINISH = 10

    def _update(self):
        if self.phase != Phase.AI_MOVE:
            return

        if self.ai_delay > 0:
            self.ai_delay -= 1
            return
        
        if self.ai_stage == AIState.THINKING:
            best_action = self.mcts.mcts_best_action(self.board)

            if not best_action:
                # if AI is stuck player wins via Victory Lap
                self.board.victory_lap()

                return
            
            self.ai_delay = self.DELAY_THINK
            self.ai_action = best_action
            self.ai_stage = AIState.MOVING
            return
        
        if self.ai_stage == AIState.MOVING:
            move, spell, target = self.ai_action
            self.board.apply_move(MageType.AI, *move)
            self.ai_delay = self.DELAY_MOVE
            self.ai_stage = AIState.CASTING_SPELL
            return

        if self.ai_stage == AIState.CASTING_SPELL:
            move, spell, target = self.ai_action

            print(f"AI Action: Move to {move}, Spell: {spell}, Target: {target}")

            if spell == Spell.BURN and not self.board.can_afford_burn(MageType.AI):
                spell = Spell.FREEZE # Downgrade to freeze if burn isn't affordable
            
            if target:
                tile = self.board.get_tile(*target)
                self.board.apply_spell(MageType.AI, spell, *target)

            self.ai_delay = self.DELAY_SPELL
            self.ai_stage = AIState.FINISHING_TURN
            return
        
        if self.ai_stage == AIState.FINISHING_TURN:
            self.board.turn_increase_cumulative_mana()
            self.board.turn_decrement_freeze_timer()
            self.ai_delay = self.DELAY_FINISH
            self.ai_action = None
            self.ai_busy = False
            self.ai_stage = AIState.THINKING
            self.update_valid_moves()

            # Check if player is trapped
            if not self.board.valid_mage_moves(*self.board.player_pos):
                self.board.victory_lap(MageType.AI)
                self._finish()
                return
            
            self.phase = Phase.PLAYER_MOVE
        


    def _update_animations(self):
        self.player.update()
        self.ai.update()


    # ===== Main Game Loop =====
    def run(self):
        while True:
            self._events()
            self._update()
            self.board_display.draw()
            self.panel_display.draw()
            
            pygame.display.flip()
            self.clock.tick(60)
            self._update_animations()

if __name__ == "__main__":
    Game().run()
        
    
    






