import pygame
from wizard import Wizard


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Arcane Duel")
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()

        size = 20
        self.wizard_red = Wizard("red", 100, size)
        self.wizard_blue = Wizard("blue", 100, size)
        self.wizard_blue.set_state("walking")

    def run(self):
        while True:
            self.screen.fill((255, 255, 255))
            self.screen.blit(self.wizard_red.get_current_frame(), (0, 0))
            self.screen.blit(self.wizard_blue.get_current_frame(), (200, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            pygame.display.update()
            self.wizard_red.update()
            self.wizard_blue.update()
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
