import pygame

class Animation:
    def __init__(self, spritesheet, row, num_frames, target_width, target_height, speed) :
        self.frames = []
        self.current_frame = 0
        self.speed = speed
        self.last_update = pygame.time.get_ticks()

        for i in range(num_frames):
            x_pos = i * spritesheet.frame_width
            y_pos = row * spritesheet.frame_height

            # Get the frame from the spritesheet
            raw_frame = spritesheet.get_image(
                x_pos, y_pos, spritesheet.frame_width, spritesheet.frame_height
            )

            # Scale the cropped frame
            scaled_frame = pygame.transform.scale(raw_frame, (target_width, target_height))

            self.frames.append(scaled_frame)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def get_current_frame(self):
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()




