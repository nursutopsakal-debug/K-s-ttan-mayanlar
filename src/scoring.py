"""
Scoring system for wedding seating game.
Evaluates a player's seating layout and returns detailed scores.
"""


def evaluate(player_layout, level_data, guests_data):
    """
    Evaluate a seating layout and return detailed scores.

    Args:
        player_layout: dict like {"Table 1": ["Emma", "John"], "Table 2": ["Sophia"]}
        level_data: dict with table settings and rules
        guests_data: list or dict of guests with properties

    Returns:
        dict with all score components and penalties
    """
    scores = {
        "happiness": 0,
        "entertainment": 0,
        "family_balance": 0,
        "vip_satisfaction": 0,
        "hidden_bonuses": 0,
        "tension": 0,
        "gossip": 0,
        "major_crisis": 0,
        "total_score": 0,
        "penalties": [],
        "has_major_violation": False
    }

    guests_dict = _get_guests_dict(guests_data)

    scores["happiness"] = _calculate_happiness(player_layout, guests_dict)
    scores["entertainment"] = _calculate_entertainment(player_layout, guests_dict)
    scores["family_balance"] = _calculate_family_balance(player_layout, guests_dict)
    scores["vip_satisfaction"] = _calculate_vip_satisfaction(player_layout, level_data, guests_dict)
    scores["hidden_bonuses"] = _calculate_hidden_bonuses(player_layout, guests_dict)
    scores["tension"] = _calculate_tension(player_layout, guests_dict)
    scores["gossip"] = _calculate_gossip(player_layout, guests_dict)
    scores["major_crisis"], violations = _check_major_crisis(player_layout, level_data, guests_dict)

    if violations:
        scores["penalties"].extend(violations)
        scores["has_major_violation"] = True

    weights = level_data.get("score_weights", {
        "happiness": 25,
        "entertainment": 15,
        "family_balance": 20,
        "vip_satisfaction": 15,
        "hidden_bonuses": 5,
        "tension": -15,
        "gossip": -10,
        "major_crisis": -50
    })

    total = 0
    for key, weight in weights.items():
        if key in scores and isinstance(scores[key], (int, float)):
            total += scores[key] * weight / 100

    scores["total_score"] = round(total, 2)
    return scores


def _get_guests_dict(guests_data):
    if isinstance(guests_data, list):
        return {g["name"]: g for g in guests_data}
    return guests_data


def _calculate_happiness(player_layout, guests_dict):
    happiness = 0
    for guests in player_layout.values():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue
            preferred = guest.get("preferred_with", [])
            for other_name in guests:
                if other_name != guest_name and other_name in preferred:
                    happiness += 10
    return happiness


def _calculate_entertainment(player_layout, guests_dict):
    score = 0
    for guests in player_layout.values():
        social_count = 0
        quiet_count = 0
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue
            tags = guest.get("tags", [])
            if "social" in tags or "funny" in tags:
                social_count += 1
            if "quiet" in tags:
                quiet_count += 1
        if social_count >= 1 and quiet_count >= 1:
            score += 8
    return score


def _calculate_family_balance(player_layout, guests_dict):
    score = 0
    families = {}
    for table, guests in player_layout.items():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue
            family = guest.get("family", "")
            if family:
                families.setdefault(family, []).append((guest_name, table))
    for members in families.values():
        if len(members) > 1:
            same_table = [m for m in members if m[1] == members[0][1]]
            if len(same_table) == len(members):
                score += 15
            else:
                score -= 8
    return score


def _calculate_vip_satisfaction(player_layout, level_data, guests_dict):
    vip_tables = level_data.get("vip_tables", [])
    score = 0
    for table, guests in player_layout.items():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue
            if guest.get("is_vip", False):
                if table in vip_tables:
                    score += 20
                else:
                    score -= 15
    return score


def _calculate_hidden_bonuses(player_layout, guests_dict):
    bonus = 0
    families = {}
    for table, guests in player_layout.items():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue
            family = guest.get("family", "")
            if family:
                families.setdefault(family, []).append((guest_name, table))
    for members in families.values():
        if len(members) > 2 and all(m[1] == members[0][1] for m in members):
            bonus += 25
    return bonus


def _calculate_tension(player_layout, guests_dict):
    tension = 0
    for guests in player_layout.values():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue
            cannot_sit = guest.get("cannot_sit_with", [])
            for other_name in guests:
                if other_name != guest_name and other_name in cannot_sit:
                    tension -= 20
    return tension


def _calculate_gossip(player_layout, guests_dict):
    gossip = 0
    for guests in player_layout.values():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue
            tags = guest.get("tags", [])
            if "ex_partner" in tags:
                for other_name in guests:
                    other = guests_dict.get(other_name)
                    if other and "ex_partner" in other.get("tags", []) and guest_name != other_name:
                        gossip -= 12
            if "rival" in tags:
                for other_name in guests:
                    other = guests_dict.get(other_name)
                    if other and "rival" in other.get("tags", []) and guest_name != other_name:
                        gossip -= 10
    return gossip


def _check_major_crisis(player_layout, level_data, guests_dict):
    violations = []
    score = 0
    seats_per_table = level_data.get("seats_per_table", 8)
    for table, guests in player_layout.items():
        if len(guests) > seats_per_table:
            violations.append(f"{table} exceeds capacity ({len(guests)} > {seats_per_table})")
            score -= 50
    for table, guests in player_layout.items():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue
            cannot_sit = guest.get("cannot_sit_with", [])
            for other_name in guests:
                if other_name in cannot_sit:
                    violations.append(f"Hard constraint broken: {guest_name} and {other_name} at {table}")
                    score -= 50
    return score, violations
