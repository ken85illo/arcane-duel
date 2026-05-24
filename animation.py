import pygame


class Animation:
    def __init__(
        self,
        frame_paths: list[str],
        img_scale: float,
        frame_duration: float,
        repeat: bool = True,
    ):
        self.frames = [
            Image(path, img_scale).get_image() for path in frame_paths
        ]
        self.frame_duration = frame_duration  # milliseconds per frame
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.repeat = repeat
        self.finished = False

    def update(self):
        if self.finished:
            return
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            if self.current_frame + 1 < len(self.frames):
                self.current_frame += 1
            elif self.repeat:
                self.current_frame = 0
            else:
                self.finished = True
            self.last_update = now

    def get_current_frame(self):
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.finished = False
        self.last_update = pygame.time.get_ticks()


class Image:
    def __init__(self, path: str, img_scale: float):
        self.original = pygame.image.load(path)
        self.image = pygame.transform.smoothscale_by(
            self.original, img_scale * 0.01
        )

    def get_image(self):
        return self.image
