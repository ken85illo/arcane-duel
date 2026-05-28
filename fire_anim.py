import math
import random

import pygame

from animation import Animation
from spritesheet import SpriteSheet
from ui_util import tile_rect


class FireAnim:
    FALL_END     = 54
    IMPACT_END = 74
    SCALE = 3
    SPRITE_WIDTH = 48 * SCALE
    SPRITE_HEIGHT = 32 * SCALE

    def __init__(self, target_pos, tile_mana, was_frozen):
        self.offset_x = -80
        self.offset_y = -90
        self.rotation = 235


        self.target_pos = target_pos
        self.tile_mana = tile_mana
        self.was_frozen = was_frozen
        self.frame = 0
        target_rect = tile_rect(*target_pos)
        self.target_pixel = (target_rect.centerx, target_rect.centery)

        fire_sprite = SpriteSheet(
            "assets/fire.png", 48, 32
        )
        self.fire_anim = Animation(
            fire_sprite,
            row = 0,
            num_frames=5,
            speed=100,
            target_width=self.SPRITE_WIDTH,
            target_height=self.SPRITE_HEIGHT
        )

        # Fire starts far above and to the right of the target
        self.start_pixel  = (target_rect.centerx + 120, -60)
    
    def anim_done(self):
        return self.frame >= self.IMPACT_END
    
    def anim_update(self):
        self.frame = min(self.frame + 1, self.IMPACT_END)

    def fire_pixel(self):
        # Position of the fire sprite
        # Ease-in function
        factor = self.frame / self.FALL_END
        
        pos_x = self.start_pixel[0] + (self.target_pixel[0] - self.start_pixel[0]) * factor
        pos_y = self.start_pixel[1] + (self.target_pixel[1] - self.start_pixel[1]) * factor
        return int(pos_x), int(pos_y)
    
    def impact_frame(self):
        # Progress of impact from 0-1
        if self.frame <= self.FALL_END:
            return 0.0
        return min((self.frame - self.FALL_END) / (self.IMPACT_END - self.FALL_END), 1.0)

        
    def draw(self, surface):
        pos_x, pos_y = self.fire_pixel()
        self.fire_anim.update()

        frame = self.fire_anim.get_current_frame()
        frame = pygame.transform.rotate(frame, self.rotation)

        surface.blit(frame, (pos_x + self.offset_x, pos_y + self.offset_y))

        
        
        



    
 

        