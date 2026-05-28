from board_display import tile_rect
from enums import MageType
from ui_util import lerp


class MoveAnim:
    FRAMES = 24

    def __init__(self, who: MageType, origin, destination):
        self.who = who
        self.origin = origin
        self.destination = destination
        self.frame = 0

    def anim_progress(self):
        raw = self.frame / self.FRAMES
        return raw * raw * (3 - 2 * raw)

    def anim_done(self):
        return self.frame >= self.FRAMES

    def anim_update(self):
        self.frame = min(self.frame + 1, self.FRAMES)

    def current_pixel(self):
        row_orig, col_orig = self.origin
        row_dest, col_dest = self.destination

        rect_origin = tile_rect(row_orig, col_orig)
        rect_dest = tile_rect(row_dest, col_dest)

        pos_x = rect_origin.x + (rect_dest.x - rect_origin.x) * self.anim_progress()
        pos_y = rect_origin.y + (rect_dest.y - rect_origin.y) * self.anim_progress()
        return int(pos_x), int(pos_y)


