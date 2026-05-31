import random
import sys
import threading
import time

from graphics.freeze_anim import FreezeAnim
from ai.mcts import MCTS
from core.enums import Phase, AIState, Winner, Direction
from core.board import Board
from core.mage import Mage, MageStates
from core.enums import MageType, Spell

from graphics.fire_anim import FireAnim
from graphics.move_anim import MoveAnim
from graphics.tile_destroy_anim import TileDestroyAnim
from graphics.transition import Transition
from ui.util import GridConfig

from ui.board_display import BoardDisplay, tile_rect
from ui.flash_display import FlashDisplay
from ui.game_over_display import GameOverDisplay
from ui.panel_display import PanelDisplay
from ui.main_menu_display import MainMenuDisplay

import pygame

class Game:
    PANEL_WIDTH = 400
    SCREEN_WIDTH = 1060    # GridConfig.GRID_SIZE * GridConfig.TILE_SIZE + PANEL_WIDTH
    SCREEN_HEIGHT = 660                 # GridConfig.GRID_SIZE * GridConfig.TILE_SIZE
    
    def _make_font(self, size, bold=False):
        font =  pygame.font.Font("assets/luckiest_guy.ttf", size)
        return font

    def _get_difficulty(self):
        difficulty = "MEDIUM"

        if self.mcts_iterations == 1000:
            difficulty = "EASY"
        elif self.mcts_iterations == 2500:
            difficulty = "MEDIUM"
        elif self.mcts_iterations == 5000:
            difficulty = "HARD"  
        
        return difficulty

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Arcane Duel")

        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )
        
        # Medium difficulty
        self.mcts_iterations = 2500

        # Compute tile size to fit the fixed window, keeping the grid square
        self._update_tile_size()

        # Font sizes for different UI elements
        self.font_xl = self._make_font(38, True)  # Scores, game-over text
        self.font_lg = self._make_font(22, True)  # Header title
        self.font_md = self._make_font(16)             # Spell buttons, mana numbers
        self.font_sm = self._make_font(13)             # Legend, combat log, labels

        self.clock = pygame.time.Clock()
        
        self.phase = Phase.MAIN_MENU
        self.main_menu_display = MainMenuDisplay(self)
    
    # ===== Game Setup =====
    def _new_game(self):
        self._update_tile_size()
        self.player = Mage(False)
        self.ai = Mage(True)
        self.phase = self._randomize_starting_turn() # Starting turn
        self.board = Board(self.player, self.ai) # Starting board
        self.hover_tile   = None # Grid position under the mouse cursor
        self.valid_player_move_set = set() # Valid movement targets for the player this turn
        self.valid_player_spell_set = set() # Valid spell targets for the player this turn
        self.spell_choice = Spell.FREEZE
        self.winner: Winner = None     
        
        self.log = [{"src": None, "msg": "[SYSTEM]: Welcome to Arcane Duel!"},
                    {"src": None, "msg": f"[SYSTEM]: {GridConfig.GRID_SIZE-2}x{GridConfig.GRID_SIZE-2} board"},
                    {"src": None, "msg": f"[SYSTEM]: AI difficulty set to {self._get_difficulty()}"},
                    {"src": None, "msg": f"[SYSTEM]: {self._get_difficulty()} = {self.mcts_iterations} iterations"}] # Combat log entries (max 9 lines)

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
        self.mcts = MCTS(self.mcts_iterations)

        # Animation lists
        self.move_anims = []
        self.fire_anims = []
        self.freeze_anims = []
        self.tile_destroy_anims = []
        self.pending_spells = []  # queued spells to apply on animation impact
        self.transition = Transition(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)


        self.update_valid_moves()

        self.victory_lap_pending = None
        self.victory_lap_completed = False
        self.victory_lap_delay = 10
        self.victory_lap_pause = 300
        self.victory_lap_timer = self.victory_lap_delay


    def _update_tile_size(self):
        GridConfig.TILE_SIZE = min(
            (self.SCREEN_WIDTH - self.PANEL_WIDTH) // GridConfig.GRID_SIZE,
            self.SCREEN_HEIGHT // GridConfig.GRID_SIZE,
        )

    def _randomize_starting_turn(self) -> Phase:
        r = random.randint(1, 100)

        return Phase.PLAYER_MOVE if r <= 50 else Phase.AI_MOVE

    def log_add(self, m):

        if m["src"] == MageType.PLAYER:
            m["msg"] = "[PLAYER]: " + m["msg"]
        elif m["src"] == MageType.AI:
            m["msg"] = "[AI]: " + m["msg"]    

        self.log.append(m)
        if len(self.log) > 15:
            self.log.pop(0)

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
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.phase = Phase.MAIN_MENU
                return

            # When Game Over, restarts on 'R' key press
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.phase == Phase.GAME_OVER:
                self._new_game()
            
            # Handles left mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.phase == Phase.MAIN_MENU:
                    self.main_menu_display.handle_click(mx, my)
                    return
                

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
                tile = self.board.get_tile(new_row, new_col)
                mana = tile.mana

                self.board.apply_move(MageType.PLAYER, new_row, new_col)
                self.update_valid_spells()
                self.move_anims.append(MoveAnim(MageType.PLAYER, old_pos, clicked_tile))
                self.tile_destroy_anims.append(TileDestroyAnim(old_pos))

                self.phase = Phase.PLAYER_SPELL # Transition to spell phase after a move
                self.spell_choice = None

                # LOG MESSAGE 
                self.log_add({"src": MageType.PLAYER, "msg": f"moves to ({new_row}, {new_col})"})
                self.log_add({"src": MageType.PLAYER, "msg": f"stepped on +{mana} mana"})
                
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
                    # LOG MESSAGE
                    self.log_add({"src": MageType.PLAYER, "msg": f"casts BURN on tile ({row}, {col})"})

                    # LOG MESSAGE
                    if tile.is_frozen():
                        self.log_add({"src": MageType.PLAYER, "msg": f"collected +{tile.mana} mana"})

                    # Play caster attack animation immediately and queue burn effect for impact
                    self._play_mage_attack(col, MageType.PLAYER)

                    self.fire_anims.append(
                        FireAnim(clicked_tile, tile.mana, tile.is_frozen())
                    )

                    self.pending_spells.append({
                        'who': MageType.PLAYER,
                        'spell': self.spell_choice,
                        'target': clicked_tile,
                    })
                else:
                    # LOG MESSAGE    
                    self.log_add({"src": MageType.PLAYER, "msg": f"casts FREEZE on tile ({row}, {col})"})

                    self._play_mage_attack(col, MageType.PLAYER)

                    self.freeze_anims.append(
                        FreezeAnim(clicked_tile)
                    )
                    self.board.apply_spell(MageType.PLAYER, self.spell_choice, row, col)

                self._end_player_turn()
        
        else:
            return # Not player's turn, do nothing

    def _play_mage_attack(self, col, who: MageType):
        sprite = self.player if who == MageType.PLAYER else self.ai
        pos = self.board.player_pos if who == MageType.PLAYER else self.board.ai_pos

        if sprite:
            sprite.set_state(MageStates.ATTACK)
            _, old_col  = pos
            if old_col != col:
                if who == MageType.PLAYER:
                    self.board.player_direction = Direction.LEFT if col < old_col else Direction.RIGHT
                else:
                    self.board.ai_directiion = Direction.LEFT if col < old_col else Direction.RIGHT
                
    def _end_player_turn(self):
        # Check if AI is trapped before next turn starts
        if self.check_game_over(MageType.AI, Phase.AI_MOVE):
            return
        
        self._flash("AI's TURN ", t=60)

        self.board.turn_increase_cumulative_mana()
        self.board.turn_decrement_freeze_timer(self.freeze_anims)

        # Start the AI's turn
        self.phase = Phase.AI_MOVE
        self.ai_busy   = True
        self.ai_stage  = AIState.START
        self.ai_delay  = 0
        self.ai_action = None
    
    def check_game_over(self, turn: MageType, phase: Phase):
        def _finish_game(victory_lap_pending):
            who, final_mana, _ = victory_lap_pending
            self._finish(who, final_mana)


        # Checks if Player still has moveable spots after AI Turn
        if turn == MageType.PLAYER and phase == Phase.PLAYER_MOVE and not self.board.valid_mage_moves(*self.board.player_pos):
            self.log_add({"src": MageType.PLAYER, "msg": "has no more possible moves!"})
            self.victory_lap_pending = self.board.victory_lap(MageType.AI) # AI Wins
            _finish_game(self.victory_lap_pending)
            return True

        # Checks if Player still has valid spell targets during spell phase
        if turn == MageType.PLAYER and phase == Phase.PLAYER_SPELL and not self.board.valid_spell_targets(*self.board.player_pos):
            self.log_add({"src": MageType.PLAYER, "msg": "has no more possible spell targets!"})
            self.victory_lap_pending = self.board.victory_lap(MageType.AI) # AI Wins
            _finish_game(self.victory_lap_pending)
            return True
        
        # Checks if AI still has moveable spots after Player Turn
        if turn == MageType.AI and phase == Phase.AI_MOVE and not self.board.valid_mage_moves(*self.board.ai_pos):
            self.log_add({"src": MageType.AI, "msg": "has no more possible moves!"})
            self.victory_lap_pending = self.board.victory_lap(MageType.PLAYER) # Player Wins
            _finish_game(self.victory_lap_pending)
            return True

        # Checks if AI still has valid spell targets during spell phase
        if turn == MageType.AI and phase == Phase.AI_SPELL and not self.board.valid_spell_targets(*self.board.ai_pos):
            self.log_add({"src": MageType.AI, "msg": "has no more possible spell targets!"})
            self.victory_lap_pending = self.board.victory_lap(MageType.PLAYER) # Player Wins
            _finish_game(self.victory_lap_pending)
            return True

        
        return False

    def _finish(self, who, final_mana):
        self._flash(f"{"Player" if who == MageType.PLAYER else "AI"} enters the victory lap", t=10)
        player_mana, ai_mana = self.board.player_mana, self.board.ai_mana
        
        if who == MageType.PLAYER:
            player_mana = final_mana
        else:
            ai_mana = final_mana

        self.winner = Winner.PLAYER if player_mana > ai_mana else (Winner.AI if ai_mana > player_mana else Winner.DRAW)

        win_sprite = self.player if self.winner == Winner.PLAYER else self.ai
        lose_sprite = self.ai if self.winner == Winner.PLAYER else self.player

        win_sprite.set_state(MageStates.WIN)
        lose_sprite.set_state(MageStates.DEATH)

        self.phase = Phase.GAME_OVER


    def _trigger_victory_lap(self):
        if self.victory_lap_pending:
            if self.victory_lap_timer > 0:
                self.victory_lap_timer -= 1
                return True

            if self.victory_lap_completed:
                self.victory_lap_completed = False
                self.victory_lap_pending = None
                return False

            if self.victory_lap_pending[0] == MageType.PLAYER:
                self.board.player_mana = min(self.board.player_mana + 1, self.victory_lap_pending[1])
                new_mana = self.board.player_mana

            elif self.victory_lap_pending[0] == MageType.AI:
                self.board.ai_mana = min(self.board.ai_mana + 1, self.victory_lap_pending[1])
                new_mana = self.board.ai_mana
            
            if new_mana >= self.victory_lap_pending[1]:
                self.victory_lap_completed = True
                self.victory_lap_timer = self.victory_lap_pause 
                return True
            
            self.victory_lap_timer = self.victory_lap_delay
            return True
        
        return False
    
    # ===== AI Logic =====

    DELAY_THINK  = 45
    DELAY_MOVE   = 100
    DELAY_SPELL  = 100
    DELAY_FINISH = 10

    def start_ai_calculation(self):
        self.ai_stage = AIState.THINKING

        def ai_calculation(board, mcts):
            try:
                best_action = mcts.mcts_best_action(board)

                self.ai_action = best_action

                if not best_action:
                    self.victory_lap_pending = self.board.victory_lap(MageType.PLAYER)
                    who, final_mana, _ = self.victory_lap_pending
                    self._finish(who, final_mana)
                    return

                self.ai_delay = self.DELAY_THINK
                self.ai_action = best_action
                self.ai_stage = AIState.MOVING

            except Exception:
                # Ignore thread errors caused by menu changes,
                # game resets, grid size changes, etc.
                return

        # Run mcts in the background
        worker = threading.Thread(target=ai_calculation, args=(self.board, self.mcts), daemon=True)
        worker.start()

        

    def _update(self):
        if self._trigger_victory_lap():
            return

        if self.flash_timer > 0 :
            self.flash_timer -= 1

        if self.phase != Phase.AI_MOVE:
            return

        if self.ai_delay > 0:
            self.ai_delay -= 1
            return
        
        # If there are active fire animations, wait for them to finish
        
        if self.fire_anims:
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
            self.tile_destroy_anims.append(TileDestroyAnim(old_pos))

            # LOG MESSAGE
            self.log_add({"src": MageType.AI, "msg": f"moves to ({move[0]}, {move[1]})"})

            if target:
                self.log_add({"src": MageType.AI, "msg": f"stepped on +{self.board.get_tile(*target).mana} mana"})

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
                if spell == Spell.BURN:
                    self._play_mage_attack(target[1], MageType.AI)
                    self.fire_anims.append(
                        FireAnim(target, tile.mana, tile.is_frozen())
                    )

                    self.pending_spells.append({
                        'who': MageType.AI,
                        'spell': spell,
                        'target': target,
                    })

                else:

                    self._play_mage_attack(target[1], MageType.AI)
                    self.freeze_anims.append(
                        FreezeAnim(target)
                    )

                    self.board.apply_spell(MageType.AI, spell, *target)



            self.ai_delay = self.DELAY_SPELL
            self.ai_stage = AIState.FINISHING_TURN
            
            # LOG MESSAGE
            if spell == Spell.FREEZE:
                self.log_add({"src": MageType.AI, "msg": f"casts FREEZE on tile ({target[0]}, {target[1]})"})

            if spell == Spell.BURN:
                self.log_add({"src": MageType.AI, "msg": f"casts BURN on tile ({target[0]}, {target[1]})"})

            if spell == Spell.BURN and self.board.get_tile(*target).is_frozen():
                self.log_add({"src": MageType.AI, "msg": f"collected +{tile.mana} mana"})

            return
        
        if self.ai_stage == AIState.FINISHING_TURN:
            # Check if Player is trapped before next turn starts
            if self.fire_anims: # Wait for fire anim to stop
                return

            if self.check_game_over(MageType.PLAYER, Phase.PLAYER_MOVE):
                return
            
            self._flash("PLAYER's TURN ", t=100)

            self.board.turn_increase_cumulative_mana()
            self.board.turn_decrement_freeze_timer(self.freeze_anims)

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

        all_anims = (
            self.move_anims, 
            self.fire_anims, 
            self.freeze_anims, 
            self.tile_destroy_anims
        )

        for anim_list in all_anims:
            for animation in anim_list:
                animation.anim_update()
            
        # Apply pending spells when their fire animation reaches impact
        remaining_pending = []
        for pending in self.pending_spells:
            target = pending['target']
            # find a matching fire anim
            matching = None
            for anim in self.fire_anims:
                if anim.target_pos == target:
                    matching = anim
                    break
            
            if matching and matching.frame >= FireAnim.IMPACT_END:
                # apply the spell effect now
                who = pending['who']
                spell = pending['spell']
                row, col = target
                self.board.apply_spell(who, spell, row, col)

                tile = self.board.get_tile(row, col)

                if not tile.is_active() and not tile.is_frozen():
                    self.tile_destroy_anims.append(TileDestroyAnim((row, col)))
            else:
                remaining_pending.append(pending)

        self.pending_spells = remaining_pending

        # Remove completed animations after applying pending spells
        for anims in all_anims:
            anims[:] = [anim for anim in anims if not anim.anim_done()]


    def _is_any_anim_running(self):
        return (self.move_anims or self.fire_anims or self.freeze_anims or self.tile_destroy_anims)
                
    # ===== Main Game Loop =====
    def run(self):
        while True:
            self._events()

            # Main menu loop
            if self.phase == Phase.MAIN_MENU:
                self.main_menu_display.draw()
                pygame.display.flip()
                self.clock.tick(60)
                
                continue

            self._update()
            self._update_animations()
            self.board_display.draw()
            self.panel_display.draw()

            if not self.transition.done():
                self.transition.draw(self.screen)
                self.transition.update()

            if self.phase == Phase.GAME_OVER and not self.victory_lap_pending:
                self.game_over_display.draw()

            if self.flash_timer > 0:
                self.flash_display.draw()

            
            pygame.display.flip()
            self.clock.tick(60)

