import json
from pathlib import Path

from src.optimizer import solve, evaluate


BASE_DIR = Path(__file__).resolve().parent


def load_json(relative_path: str):
    with open(BASE_DIR / relative_path, "r", encoding="utf-8") as file:
        return json.load(file)


def pretty_print_result(result: dict):
    print("\n=== OPTIMIZATION RESULT ===")
    print("\nLayout:")
    for table_id, guests in result["layout"].items():
        print(f"  {table_id}: {guests}")

    print("\nScore Components:")
    for key, value in result["components"].items():
        print(f"  {key}: {value}")

    print(f"\nTotal Score: {result['total_score']}")
    print(f"Penalty Trigger: {result['penalty_trigger']}")

    if result["hard_violations"]:
        print("\nHard Violations:")
        for v in result["hard_violations"]:
            print(f"  - {v}")
    else:
        print("\nNo hard violations.")


def main():
    guests_data = load_json("data/guests.json")
    levels_data = load_json("data/levels.json")

    guests = guests_data["guests"]
    level_1 = levels_data["levels"][0]

    result = solve(guests, level_1)
    pretty_print_result(result)

    # örnek player layout test
    sample_player_layout = {
        "T1": ["g10", "g11", "g1", "g2", "g3"],
        "T2": ["g4", "g5", "g6", "g7", "g12"],
        "T3": ["g8", "g9", "g13", "g14", "g15"]
    }

    print("\n=== SAMPLE PLAYER LAYOUT EVALUATION ===")
    eval_result = evaluate(sample_player_layout, guests, level_1)
    pretty_print_result(eval_result)


if __name__ == "__main__":
    main()