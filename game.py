import pygame
import sys

class MapGrid:
    # 10 rows (y), 6 columns (x)
    MAP = [
        ['x','x','x','x','x','x','x','x','x','x','x'],
        ['x',' ',' ',' ','p',' ',' ',' ',' ',' ','x'],
        ['x',' ','0',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
        ['x','x','x','x','x','x','x','x','x','x','x'],
    ]

class Game:
    TILE_SIZE = 40  # Bigger size feels great now since the window wraps perfectly

    # Sample Color. Will be changed for image sprites
    COLOR_WALL = (40, 40, 50)
    COLOR_PLAYER = (255, 255, 255)
    COLOR_OBJECT = (115, 194, 251)
    COLOR_FLOOR = (29, 28, 42)

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Arcane Duel")
        
        self.map = [row[:] for row in MapGrid.MAP]
        
        self.rows = len(self.map)         
        self.cols = len(self.map[0])    
        
        # Scale the window size to overall grid size
        self.width = self.cols * self.TILE_SIZE
        self.height = self.rows * self.TILE_SIZE
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        
        # Current player position
        self.player_x = 4
        self.player_y = 1
    
    def draw_tile_topdown(self, surface, gx, gy, color):
        x = gx * self.TILE_SIZE
        y = gy * self.TILE_SIZE
        
        rect = pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 1)  # Grid lines

    def handle_click(self, mouse_pos):
        gx = mouse_pos[0] // self.TILE_SIZE
        gy = mouse_pos[1] // self.TILE_SIZE
        
        # Bounds checking of where mouse was clicked
        if (0 <= gy < self.rows and 0 <= gx < self.cols):
            target_tile = self.map[gy][gx]
            
            # Check if the target cell is empty/walkable and adjacent
            if (target_tile == ' ' and (
                  (abs(gx - self.player_x) == 1 and abs(gy - self.player_y) == 0) or 
                  (abs(gy - self.player_y) == 1 and abs(gx - self.player_x) == 0)
                 )
                ):
                # Clear player's old position
                self.map[self.player_y][self.player_x] = ' '
                
                # Update player variables to new position
                self.player_x = gx
                self.player_y = gy
                
                # Place player token into the new map cell
                self.map[gy][gx] = 'p'

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Listen for mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button click
                        self.handle_click(event.pos)

            # Draw everything
            for gy, row in enumerate(self.map):
                for gx, tile in enumerate(row):
                    if tile == 'x':
                        tile_color = self.COLOR_WALL
                    elif tile == '0':
                        tile_color = self.COLOR_OBJECT
                    elif tile == 'p':
                        tile_color = self.COLOR_PLAYER
                    else:
                        tile_color = self.COLOR_FLOOR
                        
                    self.draw_tile_topdown(self.screen, gx, gy, tile_color)

            pygame.display.flip()
            self.clock.tick(60)
        
if __name__ == "__main__":
    Game().run()