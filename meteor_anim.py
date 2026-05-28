import math
import random

from ui_util import tile_rect


class MeteorAnim:
    FALL_END     = 24
    IMPACT_END   = 44
    SMOULDER_END = 64

    def __init__(self, target_pos, tile_mana, was_frozen):
        self.target_pos = target_pos
        self.tile_mana = tile_mana
        self.was_frozen = was_frozen
        self.frame = 0
        target_rect = tile_rect(*target_pos)
        self.target_px = (target_rect.centerx, target_rect.centery)

        # Meteor starts far above and to the right of the target
        self.start_px  = (target_rect.centerx + 120, -60)
    
    def anim_done(self):
        return self.frame >= self.SMOULDER_END
    
    def anim_update(self):
        self.frame = min(self.frame + 1, self.SMOULDER_END)

    def current_pixel(self):
        # Ease-in function
        factor = min(self.frame / self.FALL_END, 1.0)
        factor2 = factor * factor
        
        pos_x   = self.start_px[0] + (self.target_px[0] - self.start_px[0]) * factor2
        pos_y   = self.start_px[1] + (self.target_px[1] - self.start_px[1]) * factor2
        return int(pos_x), int(pos_y)
    
    def impact_frame(self):
        # Progress of impact from 0-1
        if self.frame <= self.FALL_END:
            return 0.0
        return min((self.frame - self.FALL_END) / (self.IMPACT_END - self.FALL_END), 1.0)
    
    def smoulder_frame(self):
        # Progress of smoulder from 0-1
        if self.frame <= self.IMPACT_END:
            return 0.0
        return min((self.frame - self.IMPACT_END) / (self.SMOULDER_END - self.IMPACT_END), 1.0)
        



    
 

        