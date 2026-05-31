import math
import pygame

class Transition:
    TOTAL = 100

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.frame = 0
        self.max_radius = int(math.hypot(screen_width, screen_height)) + 10

    def done(self):
        return self.frame >= self.TOTAL

    def update(self):
        self.frame += 1

    def draw(self, surface):
        factor = self.frame / self.TOTAL

        # ease-out: fast start, slow end
        factor = 1.0 - (1.0 - factor) ** 2
        radius = int(self.max_radius * factor)

        circle_pos_x = self.screen_width // 2
        circle_pos_y = self.screen_height // 2

        mask = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        mask.fill((12, 14, 26, 255))

        pygame.draw.circle(mask, (0, 0, 0, 0), (circle_pos_x, circle_pos_y), radius)
        surface.blit(mask, (0, 0))








