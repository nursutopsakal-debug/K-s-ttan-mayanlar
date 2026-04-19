import json
from pathlib import Path

from src.game_logic import GameStateManager
from src.audio import AudioManager
from src.animations import AnimationController

BASE_DIR = Path(__file__).resolve().parent


def load_json(relative_path):
    with open(BASE_DIR / relative_path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    guests_data = load_json("data/guests.json")
    levels_data = load_json("data/levels.json")

    game = GameStateManager(levels_data, guests_data)
    audio = AudioManager()
    animations = AnimationController()

    audio.load_sounds()
    audio.handle_game_event("game_start")

    game.start_game()

    print("\n=== INITIAL GAME STATE ===")
    print(game.get_display_state())

    guests = game.get_current_guests()
    if guests:
        first_guest_id = guests[0]["id"]
        print(f"\nTrying to place guest: {first_guest_id} -> Table 1")
        placement_result = game.place_guest(first_guest_id, "Table 1")
        print(placement_result)

        audio.handle_game_event("guest_placed")

        if placement_result.penalty_applied:
            audio.handle_game_event("penalty")

        hint_tables = game.get_hint_for_guest(first_guest_id)
        print("\nHint tables:", hint_tables)

        print("\nAnimation hover:")
        print(animations.trigger_guest_hover(first_guest_id))

        print("\nAnimation table highlight:")
        print(animations.trigger_table_highlight("Table 1"))

        print("\n=== UPDATED GAME STATE ===")
        print(game.get_display_state())

        if game.should_play_warning_sound():
            audio.handle_game_event("timer_warning")
        else:
            audio.handle_game_event("timer_safe")

    print("\nDev3 test finished.")


if __name__ == "__main__":
    main()