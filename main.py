import pygame
import sys

from src.optimizer import solve
from src.scoring import evaluate

# Window settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Seat the Drama"
BASE_DIR = Path(__file__).resolve().parent


def load_json(relative_path):
    with open(BASE_DIR / relative_path, "r", encoding="utf-8") as file:
        return json.load(file)


def pretty_print_layout(layout):
    print("\n=== TABLE LAYOUT ===")
    for table_name, guests in layout.items():
        print(f"{table_name}: {guests}")


def pretty_print_score(result):
    print("\n=== SCORING RESULT ===")
    for key, value in result.items():
        print(f"{key}: {value}")


def run_optimizer_test():
    guests_data = load_json("data/guests.json")
    levels_data = load_json("data/levels.json")

    for level_key in ["level_1", "level_2", "level_3"]:
        if level_key not in levels_data or level_key not in guests_data:
            print(f"\n{level_key} not found, skipping.")
            continue

        level_data = levels_data[level_key]
        guests = guests_data[level_key]

        print("\n" + "=" * 60)
        print(f"Running optimizer for {level_key}")

        layout = solve(level_data, guests)
        pretty_print_layout(layout)

        print("\nEvaluating optimizer layout")
        result = evaluate(layout, level_data, guests)
        pretty_print_score(result)


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
