import asyncio

import pygame
from core.game import Game

async def main():
    pygame.init()
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
