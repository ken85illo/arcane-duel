import pygame

class SpriteSheet:
    def __init__(self, filename, width, height, scale):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.scale = scale
        self.width = width
        self.height = height
        
    def get_image(self, x, y):
        image = pygame.Surface((self.width, self.height)).convert_alpha()
        image.blit(self.sheet, (0, 0), (x, y, self.width, self.height))
        image =  pygame.transform.scale(image, (self.width * self.scale, self.height * self.scale))
        return image

class Platform:
    MAPPING = (
        (0, 0), # Full tile
        (34, 0), # Empty tile but fully surrounded
        (68, 0), # Empty tile with tile on top, left, and bottom
        (102, 0), # Empty tile with tile on top, and bottom
        (136, 0), # Empty tile with tile on top, right, and bottom
        (0, 34), # Empty tile with tile on top, left, and right
        (34, 34), # Empty tile with tile on top, and left
        (68, 68), # Empty tile with tile on top
        (102, 34), # Empty tile with tile on top, and right
        (0, 68), # Empty tile with tile on left, and right
        (34, 68), # Empty tile with tile on left
        (68, 68), # Full empty tile
        (102, 68), # Empty tile with tile on right
        (0, 102), # Empty tile with tile on left, bottom, and right
        (34, 102), # Empty tile with tile on left, and bottom
        (68, 102), # Empty tile with tile on bottom
        (102, 102) # Empty tile with tile on right, and bottom
    )
    
    SPRITE_SHEET_DARK = SpriteSheet("assets/dark_platform.png", 34, 34, 1)
    SPRITE_SHEET_LIGHT = SpriteSheet("assets/light_platform.png", 34, 34, 1)
    
    @staticmethod
    def get_platform(mapping_index, is_dark = True):
        if is_dark:
            return Platform.SPRITE_SHEET_DARK.get_image(Platform.MAPPING[mapping_index])
        else:
            return Platform.SPRITE_SHEET_LIGHT.get_image(Platform.MAPPING[mapping_index])
        
    
    

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    clock = pygame.time.Clock()
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((255, 255, 255))

        image = Platform.get_platform(1, is_dark=True)
        screen.blit(image, (100, 100))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    
    
    
    
