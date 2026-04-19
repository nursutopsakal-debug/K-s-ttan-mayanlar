import pygame
import sys
import json
from pathlib import Path

# Window settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Seat the Drama \u2014 Wedding Chaos Optimizer"
BASE_DIR = Path(__file__).resolve().parent


def load_json(relative_path):
    with open(BASE_DIR / relative_path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    from src.game import Game
    game = Game(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        game.update(dt)
        game.render()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
