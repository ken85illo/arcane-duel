from enum import Enum, auto
import pygame
from ui_util import GridConfig
from spritesheet import SpriteSheet
from animation import Animation

class MageStates(Enum):
    IDLE = auto()
    FRONT_WALK = auto()
    SIDE_WALK = auto()
    BACK_WALK = auto()
    ATTACK = auto()
    DEATH = auto()
    WIN = auto()


class Mage:
    FRAME_WIDTH = 93
    FRAME_HEIGHT = 77

    def __init__(self, is_red=False):
        # Animation speed and scale
        self.offset_x, self.offset_y = -25, -60
        self.flip_offset_x, self.flip_offset_y = -55, -60

        crop=(18, 20, 50, 50)
        scale = GridConfig.TILE_SIZE * 2
        self.state = MageStates.IDLE


        color = "red" if is_red else "blue"

        idle_sheet = SpriteSheet(
            f"assets/{color}_wizard_idle.png",
            Mage.FRAME_WIDTH,
            Mage.FRAME_HEIGHT,
        )
        front_walk_sheet = SpriteSheet(
            f"assets/{color}_wizard_front_walk.png",
            Mage.FRAME_WIDTH,
            Mage.FRAME_HEIGHT,
        )
        back_walk_sheet = SpriteSheet(
            f"assets/{color}_wizard_back_walk.png",
            Mage.FRAME_WIDTH,
            Mage.FRAME_HEIGHT,
        )
        side_walk_sheet = SpriteSheet(
            f"assets/{color}_wizard_side_walk.png",
            Mage.FRAME_WIDTH,
            Mage.FRAME_HEIGHT,
        )
        attack_sheet = SpriteSheet(
            f"assets/{color}_wizard_attack.png",
            Mage.FRAME_WIDTH,
            Mage.FRAME_HEIGHT,
        )
        death_sheet = SpriteSheet(
            f"assets/{color}_wizard_death.png",
            Mage.FRAME_WIDTH,
            Mage.FRAME_HEIGHT,
        )

        win_sheet = SpriteSheet(
            f"assets/{color}_wizard_win.png",
            Mage.FRAME_WIDTH,
            Mage.FRAME_HEIGHT,
        )

        # Map animations to states
        self.animations = {
            MageStates.IDLE: Animation(
                idle_sheet,
                row=0,
                num_frames=7,
                target_width=scale,
                target_height=scale,
                speed=150,
                crop=crop
            ),
            MageStates.FRONT_WALK: Animation(
                front_walk_sheet,
                row=0,
                num_frames=8,
                target_width=scale,
                target_height=scale,
                speed=60,
                crop=crop
            ),
            MageStates.SIDE_WALK: Animation(
                side_walk_sheet,
                row=0,
                num_frames=8,
                target_width=scale,
                target_height=scale,
                speed=60,
                crop=crop
            ),
            MageStates.BACK_WALK: Animation(
                back_walk_sheet,
                row=0,
                num_frames=8,
                target_width=scale,
                target_height=scale,
                speed=60,
                crop=crop
            ),
            MageStates.ATTACK: Animation(
                attack_sheet,
                row=0,
                num_frames=11,
                target_width=scale,
                target_height=scale,
                speed=80,
                crop=crop
            ),
            MageStates.DEATH: Animation(
                death_sheet,
                row=0,
                num_frames=11,
                target_width=scale,
                target_height=scale,
                speed=100,
                crop=crop
            ),
            MageStates.WIN: Animation(
                win_sheet,
                row=0,
                num_frames=10,
                target_width=scale,
                target_height=scale,
                speed=100,
                crop=crop
            ),
        }

    def set_state(self, new_state: MageStates):
        if self.state != new_state:
            self.state = new_state
            self.animations[self.state].reset()

    def update(self):
        active_anim = self.animations[self.state]
        prev_frame = active_anim.current_frame

        active_anim.update()

        if self.state == MageStates.WIN:
            return

        if self.state != MageStates.DEATH and active_anim.current_frame < prev_frame:
            self.set_state(MageStates.IDLE)
        
        if self.state == MageStates.DEATH and active_anim.current_frame < prev_frame:
            active_anim.current_frame = prev_frame
        
    

    def draw(self, x, y, flip, surface):
        raw_image = self.animations[self.state].get_current_frame()

        offset_x= self.flip_offset_x  if flip else self.offset_x
        offset_y= self.flip_offset_y if flip else self.offset_y

        image = pygame.transform.flip(raw_image, flip, False)
        surface.blit(image, (x + offset_x, y + offset_y))
