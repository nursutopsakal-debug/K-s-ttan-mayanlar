import pygame
import sys

# Window settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Seat the Drama — Wedding Chaos Optimizer"


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # TODO: Initialize game state (Dev 3 - game_logic.py)
    # TODO: Initialize audio (Dev 3 - audio.py)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # TODO: Pass events to UI handler (Dev 2 - ui.py)

        # TODO: Update game logic (Dev 3 - game_logic.py)

        screen.fill((30, 20, 40))
        # TODO: Render current screen (Dev 2 - renderer.py)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
