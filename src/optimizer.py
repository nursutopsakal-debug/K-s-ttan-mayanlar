from copy import deepcopy
from itertools import combinations
from typing import Dict, List, Tuple

from src.scoring import evaluate_layout


def guest_map(guests: List[dict]) -> Dict[str, dict]:
    return {g["id"]: g for g in guests}


def empty_layout(level_data: dict) -> Dict[str, List[str]]:
    return {table["table_id"]: [] for table in level_data["tables"]}


def capacities(level_data: dict) -> Dict[str, int]:
    return {table["table_id"]: table["capacity"] for table in level_data["tables"]}


def can_place(guest_id: str, table_id: str, layout: Dict[str, List[str]], guests: List[dict], level_data: dict) -> bool:
    gmap = guest_map(guests)
    caps = capacities(level_data)

    if len(layout[table_id]) >= caps[table_id]:
        return False

    guest = gmap[guest_id]

    if guest.get("type") == "vip" and table_id not in set(level_data.get("vip_tables", [])):
        return False

    for seated in layout[table_id]:
        seated_guest = gmap[seated]

        if guest_id in seated_guest.get("cannot_sit_with", []):
            return False
        if seated in guest.get("cannot_sit_with", []):
            return False

    return True


def build_initial_order(guests: List[dict], level_data: dict) -> List[str]:
    """
    Önce VIP'ler, sonra ex'ler, sonra must_sit_with olanlar, sonra diğerleri
    """
    def priority(g: dict) -> Tuple[int, int, int]:
        vip_priority = 0 if g["type"] == "vip" else 1
        ex_priority = 0 if g["type"] == "ex" else 1
        must_count = -len(g.get("must_sit_with", []))
        return (vip_priority, ex_priority, must_count)

    ordered = sorted(guests, key=priority)
    return [g["id"] for g in ordered if g["id"] in level_data["guest_ids"]]


def greedy_construct(guests: List[dict], level_data: dict) -> Dict[str, List[str]]:
    gmap = guest_map(guests)
    layout = empty_layout(level_data)
    table_ids = [t["table_id"] for t in level_data["tables"]]
    ordered_guest_ids = build_initial_order(guests, level_data)

    for gid in ordered_guest_ids:
        best_table = None
        best_score = None

        for tid in table_ids:
            if not can_place(gid, tid, layout, guests, level_data):
                continue

            trial = deepcopy(layout)
            trial[tid].append(gid)
            result = evaluate_layout(trial, guests, level_data)

            if best_score is None or result["total_score"] > best_score:
                best_score = result["total_score"]
                best_table = tid

        if best_table is not None:
            layout[best_table].append(gid)
        else:
            # zorunlu fallback: ilk boş yer
            for tid in table_ids:
                if len(layout[tid]) < capacities(level_data)[tid]:
                    layout[tid].append(gid)
                    break

    return layout


def local_search(layout: Dict[str, List[str]], guests: List[dict], level_data: dict, max_iter: int = 100) -> Dict[str, List[str]]:
    best_layout = deepcopy(layout)
    best_eval = evaluate_layout(best_layout, guests, level_data)

    table_ids = list(best_layout.keys())

    improved = True
    iteration = 0

    while improved and iteration < max_iter:
        improved = False
        iteration += 1

        # 1) Tek kişiyi başka masaya taşı
        for from_table in table_ids:
            for guest_id in list(best_layout[from_table]):
                for to_table in table_ids:
                    if from_table == to_table:
                        continue

                    trial = deepcopy(best_layout)
                    trial[from_table].remove(guest_id)

                    if len(trial[to_table]) >= capacities(level_data)[to_table]:
                        continue

                    trial[to_table].append(guest_id)
                    result = evaluate_layout(trial, guests, level_data)

                    if result["total_score"] > best_eval["total_score"]:
                        best_layout = trial
                        best_eval = result
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break

        if improved:
            continue

        # 2) Kişileri swap et
        for t1, t2 in combinations(table_ids, 2):
            for g1 in list(best_layout[t1]):
                for g2 in list(best_layout[t2]):
                    trial = deepcopy(best_layout)
                    trial[t1].remove(g1)
                    trial[t2].remove(g2)
                    trial[t1].append(g2)
                    trial[t2].append(g1)

                    result = evaluate_layout(trial, guests, level_data)
                    if result["total_score"] > best_eval["total_score"]:
                        best_layout = trial
                        best_eval = result
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break

    return best_layout


def solve(guests: List[dict], level_data: dict) -> dict:
    """
    En iyi yerleşimi üretir.
    """
    initial_layout = greedy_construct(guests, level_data)
    improved_layout = local_search(initial_layout, guests, level_data)
    result = evaluate_layout(improved_layout, guests, level_data)
    return result


def evaluate(player_layout: Dict[str, List[str]], guests: List[dict], level_data: dict) -> dict:
    """
    Oyuncunun yerleşimini puanlar.
    """
    return evaluate_layout(player_layout, guests, level_data)