from collections import defaultdict
from typing import Dict, List, Tuple


def build_guest_map(guests: List[dict]) -> Dict[str, dict]:
    return {guest["id"]: guest for guest in guests}


def invert_layout(layout: Dict[str, List[str]]) -> Dict[str, str]:
    """
    table -> guests  ==> guest -> table
    """
    guest_to_table = {}
    for table_id, guest_ids in layout.items():
        for guest_id in guest_ids:
            guest_to_table[guest_id] = table_id
    return guest_to_table


def same_table(g1: str, g2: str, guest_to_table: Dict[str, str]) -> bool:
    return guest_to_table.get(g1) is not None and guest_to_table.get(g1) == guest_to_table.get(g2)


def check_capacity(layout: Dict[str, List[str]], tables: List[dict]) -> List[str]:
    violations = []
    cap_map = {t["table_id"]: t["capacity"] for t in tables}
    for table_id, seated_guests in layout.items():
        if len(seated_guests) > cap_map.get(table_id, 0):
            violations.append(f"Capacity exceeded at {table_id}")
    return violations


def check_duplicate_or_missing(layout: Dict[str, List[str]], expected_guest_ids: List[str]) -> List[str]:
    violations = []
    all_assigned = []
    for guests in layout.values():
        all_assigned.extend(guests)

    if len(all_assigned) != len(set(all_assigned)):
        violations.append("A guest is assigned more than once")

    if set(all_assigned) != set(expected_guest_ids):
        missing = set(expected_guest_ids) - set(all_assigned)
        extra = set(all_assigned) - set(expected_guest_ids)
        if missing:
            violations.append(f"Missing guests: {sorted(list(missing))}")
        if extra:
            violations.append(f"Unknown guests assigned: {sorted(list(extra))}")

    return violations


def check_hard_constraints(layout: Dict[str, List[str]], guests: List[dict], level_data: dict) -> List[str]:
    violations = []

    tables = level_data["tables"]
    vip_tables = set(level_data.get("vip_tables", []))
    expected_guest_ids = level_data["guest_ids"]

    guest_map = build_guest_map(guests)
    guest_to_table = invert_layout(layout)

    violations.extend(check_capacity(layout, tables))
    violations.extend(check_duplicate_or_missing(layout, expected_guest_ids))

    for guest_id in expected_guest_ids:
        if guest_id not in guest_to_table:
            continue

        guest = guest_map[guest_id]

        for other_id in guest.get("cannot_sit_with", []):
            if same_table(guest_id, other_id, guest_to_table):
                violations.append(f"{guest_id} cannot sit with {other_id}")

        for other_id in guest.get("must_sit_with", []):
            if other_id in guest_to_table and not same_table(guest_id, other_id, guest_to_table):
                violations.append(f"{guest_id} must sit with {other_id}")

        if guest.get("type") == "vip":
            if guest_to_table[guest_id] not in vip_tables:
                violations.append(f"VIP guest {guest_id} must sit at a VIP table")

    return violations


def score_happiness(layout: Dict[str, List[str]], guests: List[dict]) -> int:
    guest_map = build_guest_map(guests)
    guest_to_table = invert_layout(layout)
    score = 0

    for guest in guests:
        gid = guest["id"]
        for liked in guest.get("likes", []):
            if same_table(gid, liked, guest_to_table):
                score += 2
        for disliked in guest.get("dislikes", []):
            if same_table(gid, disliked, guest_to_table):
                score -= 3

    return score


def score_entertainment(layout: Dict[str, List[str]], guests: List[dict]) -> int:
    guest_map = build_guest_map(guests)
    score = 0

    for table_id, guest_ids in layout.items():
        types = {guest_map[g]["type"] for g in guest_ids if g in guest_map}
        if len(types) >= 3:
            score += 3
        elif len(types) == 2:
            score += 1

    return score


def score_family_balance(layout: Dict[str, List[str]], guests: List[dict]) -> int:
    guest_map = build_guest_map(guests)
    score = 0

    for table_id, guest_ids in layout.items():
        bride_family = 0
        groom_family = 0
        for gid in guest_ids:
            groups = guest_map[gid].get("groups", [])
            if "bride_family" in groups:
                bride_family += 1
            if "groom_family" in groups:
                groom_family += 1

        diff = abs(bride_family - groom_family)
        if bride_family > 0 and groom_family > 0:
            score += max(0, 4 - diff)

    return score


def score_vip_satisfaction(layout: Dict[str, List[str]], guests: List[dict], level_data: dict) -> int:
    guest_map = build_guest_map(guests)
    guest_to_table = invert_layout(layout)
    vip_tables = set(level_data.get("vip_tables", []))

    score = 0
    for guest in guests:
        if guest.get("type") == "vip":
            if guest_to_table.get(guest["id"]) in vip_tables:
                score += 5
            else:
                score -= 5
    return score


def score_hidden_bonuses(layout: Dict[str, List[str]], guests: List[dict]) -> int:
    guest_map = build_guest_map(guests)
    guest_to_table = invert_layout(layout)
    score = 0

    for guest in guests:
        gid = guest["id"]
        if guest.get("type") == "friend":
            liked_count = 0
            for liked in guest.get("likes", []):
                if same_table(gid, liked, guest_to_table):
                    liked_count += 1
            if liked_count >= 1:
                score += 1

    return score


def score_tension(layout: Dict[str, List[str]], guests: List[dict]) -> int:
    guest_map = build_guest_map(guests)
    guest_to_table = invert_layout(layout)
    tension = 0

    for guest in guests:
        gid = guest["id"]
        for disliked in guest.get("dislikes", []):
            if same_table(gid, disliked, guest_to_table):
                tension += 2

    return tension


def score_gossip(layout: Dict[str, List[str]], guests: List[dict]) -> int:
    guest_map = build_guest_map(guests)
    guest_to_table = invert_layout(layout)
    gossip = 0

    for guest in guests:
        if guest.get("type") == "ex":
            for other in guests:
                if other["id"] != guest["id"] and same_table(guest["id"], other["id"], guest_to_table):
                    gossip += 1

    return gossip


def score_major_crisis(layout: Dict[str, List[str]], guests: List[dict], level_data: dict) -> int:
    hard_violations = check_hard_constraints(layout, guests, level_data)
    return len(hard_violations)


def evaluate_layout(layout: Dict[str, List[str]], guests: List[dict], level_data: dict) -> dict:
    weights = level_data["weights"]
    hard_violations = check_hard_constraints(layout, guests, level_data)

    components = {
        "happiness": score_happiness(layout, guests),
        "entertainment": score_entertainment(layout, guests),
        "family_balance": score_family_balance(layout, guests),
        "vip_satisfaction": score_vip_satisfaction(layout, guests, level_data),
        "hidden_bonuses": score_hidden_bonuses(layout, guests),
        "tension": score_tension(layout, guests),
        "gossip": score_gossip(layout, guests),
        "major_crisis": score_major_crisis(layout, guests, level_data)
    }

    total_score = (
        components["happiness"] * weights["happiness"] +
        components["entertainment"] * weights["entertainment"] +
        components["family_balance"] * weights["family_balance"] +
        components["vip_satisfaction"] * weights["vip_satisfaction"] +
        components["hidden_bonuses"] * weights["hidden_bonuses"] +
        components["tension"] * weights["tension"] +
        components["gossip"] * weights["gossip"] +
        components["major_crisis"] * weights["major_crisis"]
    )

    penalty_trigger = len(hard_violations) > 0

    return {
        "layout": layout,
        "components": components,
        "hard_violations": hard_violations,
        "penalty_trigger": penalty_trigger,
        "total_score": total_score
    }