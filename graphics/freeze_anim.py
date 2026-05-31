
class FreezeAnim:
    FREEZE_END = 120

    def __init__(self, target_pos):
        self.target_pos = target_pos
        self.frame      = 0

    def anim_done(self):
        return self.frame >= self.FREEZE_END

    def anim_update(self):
        self.frame = min(self.frame + 1, self.FREEZE_END)

    def freeze_frame(self):
        return min(self.frame / self.FREEZE_END, 1.0)
