import pygame
from spritesheet import SpriteSheet


class Platform:
    MAPPING = (
        (0, 0),  # Full tile
        (34, 0),  # Empty tile but fully surrounded
        (68, 0),  # Empty tile with tile on top, left, and bottom
        (102, 0),  # Empty tile with tile on top, and bottom
        (136, 0),  # Empty tile with tile on top, right, and bottom
        (0, 34),  # Empty tile with tile on top, left, and right
        (34, 34),  # Empty tile with tile on top, and left
        (68, 34),  # Empty tile with tile on top
        (102, 34),  # Empty tile with tile on top, and right
        (0, 68),  # Empty tile with tile on left, and right
        (34, 68),  # Empty tile with tile on left
        (68, 68),  # Full empty tile
        (102, 68),  # Empty tile with tile on right
        (0, 102),  # Empty tile with tile on left, bottom, and right
        (34, 102),  # Empty tile with tile on left, and bottom
        (68, 102),  # Empty tile with tile on bottom
        (102, 102),  # Empty tile with tile on right, and bottom
    )

    SPRITE_SHEET_DARK = SpriteSheet("assets/dark_grass_platform.png", 34, 34)
    SPRITE_SHEET_LIGHT = SpriteSheet("assets/light_grass_platform.png", 34, 34)

    @staticmethod
    def get_platform(mapping_index, width, height, is_dark=True):
        x, y = Platform.MAPPING[mapping_index]
        if is_dark:
            return Platform.SPRITE_SHEET_DARK.get_image(x, y, width, height)
        else:
            return Platform.SPRITE_SHEET_LIGHT.get_image(x, y, width, height)


