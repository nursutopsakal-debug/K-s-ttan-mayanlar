import json
from pathlib import Path

from src.optimizer import solve
from src.scoring import evaluate


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


def main():
    guests_data = load_json("data/guests.json")
    levels_data = load_json("data/levels.json")

    level_data = levels_data["level_1"]
    guests = guests_data["level_1"]

    print("Running optimizer for Level 1")
    layout = solve(level_data, guests)
    pretty_print_layout(layout)

    sample_layout = {
        "Table 1": ["Emma", "John", "Sophia", "Isabella", "Mason"],
        "Table 2": ["Liam", "Olivia", "Noah", "Ava", "Lucas"],
        "Table 3": ["Charlotte", "Benjamin", "Mia", "Ethan", "Grace"]
    }

    print("\nEvaluating sample player layout")
    result = evaluate(sample_layout, level_data, guests)
    pretty_print_score(result)


if __name__ == "__main__":
    main()
