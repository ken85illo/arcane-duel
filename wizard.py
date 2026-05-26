from enum import Enum, auto
import pygame
from spritesheet import SpriteSheet
from animation import Animation

class WizardStates(Enum):
    IDLE = auto()
    FRONT_WALK = auto()
    SIDE_WALK_RIGHT = auto()
    SIDE_WALK_LEFT = auto()
    BACK_WALK = auto()
    ATTACK = auto()
    DEATH = auto()


class Wizard:
    FRAME_WIDTH = 93
    FRAME_HEIGHT = 77

    def __init__(self, x, y, is_red=False, scale_w=120, scale_h=100, speed=4):
        # Positional tracking
        self.pos = pygame.Vector2(x, y)
        self.speed = speed
        self.scale_w = scale_w
        self.scale_h = scale_h

        self.state = WizardStates.IDLE

        color = "red" if is_red else "blue"

        idle_sheet = SpriteSheet(
            f"assets/{color}_wizard_idle.png",
            Wizard.FRAME_WIDTH,
            Wizard.FRAME_HEIGHT,
        )
        front_walk_sheet = SpriteSheet(
            f"assets/{color}_wizard_front_walk.png",
            Wizard.FRAME_WIDTH,
            Wizard.FRAME_HEIGHT,
        )
        back_walk_sheet = SpriteSheet(
            f"assets/{color}_wizard_back_walk.png",
            Wizard.FRAME_WIDTH,
            Wizard.FRAME_HEIGHT,
        )
        side_walk_sheet = SpriteSheet(
            f"assets/{color}_wizard_side_walk.png",
            Wizard.FRAME_WIDTH,
            Wizard.FRAME_HEIGHT,
        )
        attack_sheet = SpriteSheet(
            f"assets/{color}_wizard_attack.png",
            Wizard.FRAME_WIDTH,
            Wizard.FRAME_HEIGHT,
        )
        death_sheet = SpriteSheet(
            f"assets/{color}_wizard_death.png",
            Wizard.FRAME_WIDTH,
            Wizard.FRAME_HEIGHT,
        )

        # Map animations to states
        self.animations = {
            WizardStates.IDLE: Animation(
                idle_sheet,
                row=0,
                num_frames=4,
                target_width=scale_w,
                target_height=scale_h,
                speed=150,
            ),
            WizardStates.FRONT_WALK: Animation(
                front_walk_sheet,
                row=0,
                num_frames=4,
                target_width=scale_w,
                target_height=scale_h,
                speed=120,
            ),
            WizardStates.SIDE_WALK_RIGHT: Animation(
                side_walk_sheet,
                row=0,
                num_frames=4,
                target_width=scale_w,
                target_height=scale_h,
                speed=120,
            ),
            WizardStates.SIDE_WALK_LEFT: Animation(
                side_walk_sheet,
                row=0,
                num_frames=4,
                target_width=scale_w,
                target_height=scale_h,
                speed=120,
            ),
            WizardStates.BACK_WALK: Animation(
                back_walk_sheet,
                row=0,
                num_frames=4,
                target_width=scale_w,
                target_height=scale_h,
                speed=120,
            ),
            WizardStates.ATTACK: Animation(
                attack_sheet,
                row=0,
                num_frames=6,
                target_width=scale_w,
                target_height=scale_h,
                speed=80,
            ),
            WizardStates.DEATH: Animation(
                death_sheet,
                row=0,
                num_frames=8,
                target_width=scale_w,
                target_height=scale_h,
                speed=200,
            ),
        }

    def set_state(self, new_state: WizardStates):
        if self.state != new_state:
            self.state = new_state
            self.animations[self.state].reset()

    def update(self):
        active_anim = self.animations[self.state]
        active_anim.update()


    def draw(self, surface: pygame.Surface):
        raw_image = self.animations[self.state].get_current_frame()

        image = pygame.transform.flip(raw_image, self.state == WizardStates.SIDE_WALK_LEFT, False)

        rect = image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        surface.blit(image, rect.topleft)
