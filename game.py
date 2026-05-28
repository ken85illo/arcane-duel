import random
import sys
import threading

from mcts import MCTS
from enums import Phase, AIState, Winner
from board import Board
from board_display import BoardDisplay, tile_rect
from flash_display import FlashDisplay
from game_over_display import GameOverDisplay
from mage import Mage
from board import Board
from enums import MageType, Spell, Winner

from fire_anim import FireAnim
from move_anim import MoveAnim
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
        self.phase = Phase.PLAYER_MOVE # self._randomize_starting_turn() # Starting turn
        self.board = Board(self.player, self.ai) # Starting board
        self.hover_tile   = None # Grid position under the mouse cursor
        self.valid_player_move_set = set() # Valid movement targets for the player this turn
        self.valid_player_spell_set = set() # Valid spell targets for the player this turn
        self.spell_choice = Spell.FREEZE
        self.winner: Winner = None     
        # == To Be Added
        # self.log = [] # Combat log entries (max 9 lines)

        self.board_display = BoardDisplay(self)
        self.panel_display = PanelDisplay(self)
        self.flash_display = FlashDisplay(self) # For displaying temporary messages like "Invalid Move" or "AI is Thinking"
        self.game_over_display = GameOverDisplay(self)

        self.flash_msg    = "TEST"             # Short message shown in the center of the board
        self.flash_timer  = 0             # How many frames the flash message remains visible

        self.ai_busy = False
        self.ai_delay = 0
        self.ai_calculating = False
        self.ai_stage = AIState.START
        self.ai_action  = None
        self.mcts = MCTS()

        # Animation lists
        self.move_anims = []
        self.fire_anims = []
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
                if self._is_any_anim_running():
                    return # Wait for the animation

                if self.phase == Phase.PLAYER_MOVE:  
                    self._handle_player_click(mx, my)

                if self.phase == Phase.PLAYER_SPELL:
                    self._handle_player_click(mx, my)
    
    def _handle_player_click(self, mx, my):
        clicked_tile = self._tile_at(mx, my)

        if self.phase == Phase.GAME_OVER:
            return

        if self.phase == Phase.PLAYER_MOVE:
            if clicked_tile and clicked_tile in self.valid_player_move_set:
                old_pos = self.board.player_pos
                new_row, new_col = clicked_tile

                self.board.apply_move(MageType.PLAYER, new_row, new_col)
                self.update_valid_spells()
                self.move_anims.append(MoveAnim(MageType.PLAYER, old_pos, clicked_tile))
                self.phase = Phase.PLAYER_SPELL # Transition to spell phase after a move
                self.spell_choice = None
                
                self._flash("Player Spell Phase", t=60)
            else:
                self._flash("Invalid Move", t=60)
                return # Invalid move, do nothing
        
        elif self.phase == Phase.PLAYER_SPELL:
            # Check if Player is trapped before spell phase
            if self.check_game_over(MageType.PLAYER, Phase.PLAYER_SPELL): 
                return
            
            freeze_btn, burn_btn = self.panel_display._btn_rects()

            # Clicked the FREEZE button
            if freeze_btn.collidepoint(mx, my):
                self.spell_choice = Spell.FREEZE
                self._flash("Freeze Spell Selected", t=60)
                return

            # Clicked the BURN button
            if burn_btn.collidepoint(mx, my):
                if not self.board.can_afford_burn(MageType.PLAYER):
                    self._flash("Need 3 Mana for Burn Spell", t=60)
                    return
                
                self.spell_choice = Spell.BURN
                self._flash("Burn Spell Selected", t=60)
                return

            # Click a tile after selecting a spell
            if clicked_tile:

                if not self.spell_choice:
                    self._flash("Please Pick a Spell", t=60)
                    return # No spell selected, do nothing

                if clicked_tile not in self.valid_player_spell_set:
                    self._flash("Invalid Spell Target", t=60)
                    return # Invalid spell target, do nothing
                    
                row, col = clicked_tile
                tile = self.board.get_tile(row, col)

                if tile.is_frozen() and self.spell_choice == Spell.FREEZE:
                    self._flash("Tile is Already Frozen", t=60)
                    return # Can't freeze a tile that's already frozen, do nothing

                if self.spell_choice == Spell.BURN and not self.board.can_afford_burn(MageType.PLAYER):
                    self.spell_choice = None # Reset spell choice since burn can't be cast
                    self._flash("Need 3 Mana for Burn Spell", t=60)
                    return # DOUBLE CHECK. Can't afford burn, do nothing
                
                if self.spell_choice == Spell.BURN:
                    self.fire_anims.append(
                        FireAnim(clicked_tile, tile.mana, tile.is_frozen())
                    )

                self.board.apply_spell(MageType.PLAYER, self.spell_choice, row, col)
                self._end_player_turn()
        
        else:
            return # Not player's turn, do nothing

    def _end_player_turn(self):
        # Check if AI is trapped before next turn starts
        if self.check_game_over(MageType.AI, Phase.AI_MOVE):
            return
        
        self._flash("AI's TURN ", t=60)

        self.board.turn_increase_cumulative_mana()
        self.board.turn_decrement_freeze_timer()

        # Start the AI's turn
        self.phase = Phase.AI_MOVE
        self.ai_busy   = True
        self.ai_stage  = AIState.START
        self.ai_delay  = 0
        self.ai_action = None
    
    def check_game_over(self, turn: MageType, phase: Phase):
        # Checks if Player still has moveable spots after AI Turn
        if turn == MageType.PLAYER and not self.board.valid_mage_moves(*self.board.player_pos):
            self.board.victory_lap(MageType.AI) # AI Wins
            self._finish()
            return True
        
        # Checks if Player still has valid spell targets during spell phase
        if turn == MageType.PLAYER and phase == Phase.PLAYER_SPELL and not self.board.valid_spell_targets(*self.board.player_pos):
            self.board.victory_lap(MageType.AI) # AI Wins
            self._finish()
            return True
        
        # Checks if AI still has moveable spots after Player Turn
        if turn == MageType.AI and not self.board.valid_mage_moves(*self.board.ai_pos):
            self.board.victory_lap(MageType.PLAYER) # Player Wins
            self._finish()
            return True

        # Checks if AI still has valid spell targets during spell phase
        if turn == MageType.AI and phase == Phase.AI_SPELL and not self.board.valid_spell_targets(*self.board.ai_pos):
            self.board.victory_lap(MageType.PLAYER) # Player Wins
            self._finish()
            return True
        
        return False

    def _finish(self):
        player_mana, ai_mana = self.board.player_mana, self.board.ai_mana
        self.winner = Winner.PLAYER if player_mana > ai_mana else (Winner.AI if ai_mana > player_mana else Winner.DRAW)
        self.phase = Phase.GAME_OVER
    
    # ===== AI Logic =====

    DELAY_THINK  = 45
    DELAY_MOVE   = 100
    DELAY_SPELL  = 100
    DELAY_FINISH = 10


    def start_ai_calculation(self):
        self.ai_stage = AIState.THINKING

        def ai_calculation(board, mcts):
            best_action = mcts.mcts_best_action(board)
            self.ai_action = best_action

            if not best_action:
                # if AI is stuck player wins via Victory Lap
                self.board.victory_lap(MageType.PLAYER)
                self._finish()
                return
            
            self.ai_delay = self.DELAY_THINK
            self.ai_action = best_action
            self.ai_stage = AIState.MOVING

        # Run mcts in the background
        worker = threading.Thread(target=ai_calculation, args=(self.board, self.mcts), daemon=True)
        worker.start()


    def _update(self):
        if self.flash_timer > 0 :
            self.flash_timer -= 1

        if self.phase != Phase.AI_MOVE:
            return

        if self.ai_delay > 0:
            self.ai_delay -= 1
            return
        
        if self.ai_stage == AIState.START:
            self.start_ai_calculation()
            return

        if self.ai_stage == AIState.THINKING:
            self._flash("AI is thinking ", t=10)
            return
        
        if self.ai_stage == AIState.MOVING:
            self._flash("AI Movement Phase ", t=60)

            old_pos = self.board.ai_pos
            move, spell, target = self.ai_action

            self.board.apply_move(MageType.AI, *move)
            self.ai_delay = self.DELAY_MOVE
            self.ai_stage = AIState.CASTING_SPELL
            self.move_anims.append(MoveAnim(MageType.AI, old_pos, move))
            return

        if self.ai_stage == AIState.CASTING_SPELL:
            # Check if AI is trapped before spell phase
            if self.check_game_over(MageType.AI, Phase.AI_SPELL): 
                return 
            
            self._flash("AI Spell Phase", t=60)

            move, spell, target = self.ai_action
            valid_targets = self.board.valid_spell_targets(*self.board.ai_pos)

            target = target if target in valid_targets else (random.choice(valid_targets) if valid_targets else None)
            print(f"AI Action: Move to {move}, Spell: {spell}, Target: {target}")



            if spell == Spell.BURN and not self.board.can_afford_burn(MageType.AI):
                spell = Spell.FREEZE # Downgrade to freeze if burn isn't affordable
            
            if target:
                tile = self.board.get_tile(*target)
                self.board.apply_spell(MageType.AI, spell, *target)

                if spell == Spell.BURN:
                    self.fire_anims.append(
                        FireAnim(target, tile.mana, tile.is_frozen())
                    )

            self.ai_delay = self.DELAY_SPELL
            self.ai_stage = AIState.FINISHING_TURN
            return
        
        if self.ai_stage == AIState.FINISHING_TURN:
            # Check if Player is trapped before next turn starts
            if self.fire_anims: # Wait for fire anim to stop
                return

            if self.check_game_over(MageType.PLAYER, Phase.PLAYER_MOVE):
                return
            
            self._flash("PLAYER's TURN ", t=100)

            self.board.turn_increase_cumulative_mana()
            self.board.turn_decrement_freeze_timer()
            self.ai_delay = self.DELAY_FINISH
            self.ai_action = None
            self.ai_busy = False
            self.ai_stage = AIState.THINKING
            self.update_valid_moves()
            
            self.phase = Phase.PLAYER_MOVE

    def _flash(self, msg, t=100):
        self.flash_msg = msg
        self.flash_timer = t    

    def _update_animations(self):
        self.player.update()
        self.ai.update()

        for animation in self.move_anims:     
            animation.anim_update()

        for animation in self.fire_anims:
            animation.anim_update()
            
        self.move_anims = [animation for animation in self.move_anims if not animation.anim_done()]
        self.fire_anims = [animation for animation in self.fire_anims if not animation.anim_done()]


    def _is_any_anim_running(self):
        return (self.move_anims or self.fire_anims)
                
    # ===== Main Game Loop =====
    def run(self):
        while True:
            self._events()
            self._update()
            self._update_animations()
            self.board_display.draw()
            self.panel_display.draw()

            if self.phase == Phase.GAME_OVER:
                self.game_over_display.draw()

            if self.flash_timer > 0:
                self.flash_display.draw()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    Game().run()
        
    
    






