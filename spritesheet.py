import pygame


class SpriteSheet:
    def __init__(self, path, frame_width, frame_height):
        self.sheet = None
        self.path = path
        self.frame_width = frame_width
        self.frame_height = frame_height

    def get_image(self, x, y, width, height):
        if not self.sheet:
            self.sheet = pygame.image.load(self.path).convert_alpha()

        image = pygame.Surface(
            (self.frame_width, self.frame_height)
        ).convert_alpha()
        image.blit(
            self.sheet, (0, 0), (x, y, self.frame_width, self.frame_height)
        )

        image = pygame.transform.scale(image, (width, height))
        return image
