class TileDestroyAnim:
    TOTAL = 60
    TILE_COLOR = (133, 188, 74)

    def __init__(self, pos):
        self.pos = pos
        self.tile_color = self.TILE_COLOR
        self.frame = 0

    def anim_done(self):
        return self.frame >= self.TOTAL

    def anim_update(self):
        self.frame = min(self.frame + 1, self.TOTAL)

    def anim_frame(self):
        #Scale from 1.0 down to 0.0
        factor = self.frame / self.TOTAL
        return 1.0 - (factor * factor)   # ease-in collapse
