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

    weights = level_data.get(
        "score_weights",
        {
            "happiness": 25,
            "entertainment": 15,
            "family_balance": 20,
            "vip_satisfaction": 15,
            "hidden_bonuses": 5,
            "tension": -15,
            "gossip": -10,
            "major_crisis": -50
        }
    )

    total = 0
    for key, weight in weights.items():
        if key in scores and isinstance(scores[key], (int, float)):
            total += scores[key] * weight / 100

    scores["total_score"] = round(total, 2)
    return scores


def evaluate_layout(player_layout, guests_data, level_data):
    """
    Compatibility wrapper for Developer 3.
    """
    result = evaluate(player_layout, level_data, guests_data)

    return {
        "total_score": result["total_score"],
        "penalties": result["penalties"],
        "has_major_violation": result["has_major_violation"],
        "hard_violations": result["penalties"],
        "components": {
            "happiness": result["happiness"],
            "entertainment": result["entertainment"],
            "family_balance": result["family_balance"],
            "vip_satisfaction": result["vip_satisfaction"],
            "hidden_bonuses": result["hidden_bonuses"],
            "tension": result["tension"],
            "gossip": result["gossip"],
            "major_crisis": result["major_crisis"],
        },
        "layout": player_layout
    }


def _get_guests_dict(guests_data):
    if isinstance(guests_data, list):
        # Build id-to-name map for resolving references
        id_to_name = {g.get("id", g["name"]): g["name"] for g in guests_data}
        result = {}
        for g in guests_data:
            resolved = dict(g)
            # Resolve id-based references to names
            for field in ("likes", "dislikes", "must_sit_with", "cannot_sit_with"):
                if field in resolved:
                    resolved[field] = [id_to_name.get(ref, ref) for ref in resolved[field]]
            result[g["name"]] = resolved
        return result
    return guests_data


def _calculate_happiness(player_layout, guests_dict):
    happiness = 0

    for guests in player_layout.values():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue

            liked_people = guest.get("likes", [])
            must_people = guest.get("must_sit_with", [])

            for other_name in guests:
                if other_name == guest_name:
                    continue
                if other_name in liked_people:
                    happiness += 10
                if other_name in must_people:
                    happiness += 15

    return happiness


def _calculate_entertainment(player_layout, guests_dict):
    score = 0

    for guests in player_layout.values():
        types_at_table = set()
        groups_at_table = set()

        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue

            guest_type = guest.get("type")
            if guest_type:
                types_at_table.add(guest_type)

            for group in guest.get("groups", []):
                groups_at_table.add(group)

        if len(types_at_table) >= 2:
            score += 6
        if len(groups_at_table) >= 2:
            score += 4

    return score


def _calculate_family_balance(player_layout, guests_dict):
    score = 0
    families = {}

    for table, guests in player_layout.items():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue

            for group in guest.get("groups", []):
                if "family" in group:
                    families.setdefault(group, []).append((guest_name, table))

    for members in families.values():
        if len(members) > 1:
            same_table = [m for m in members if m[1] == members[0][1]]
            if len(same_table) == len(members):
                score += 15
            else:
                score -= 5

    return score


def _calculate_vip_satisfaction(player_layout, level_data, guests_dict):
    vip_tables = set(level_data.get("vip_tables", []))
    score = 0

    for table, guests in player_layout.items():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue

            is_vip = guest.get("type") == "vip" or "vip" in guest.get("groups", [])

            if is_vip:
                if table in vip_tables:
                    score += 20
                else:
                    score -= 10

    return score


def _calculate_hidden_bonuses(player_layout, guests_dict):
    bonus = 0

    for table, guests in player_layout.items():
        bride_side = 0
        groom_side = 0

        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue

            groups = guest.get("groups", [])
            if any("bride" in g for g in groups):
                bride_side += 1
            if any("groom" in g for g in groups):
                groom_side += 1

        if bride_side > 0 and groom_side > 0:
            bonus += 8

        if len(guests) >= 4:
            bonus += 5

    return bonus


def _calculate_tension(player_layout, guests_dict):
    tension = 0

    for guests in player_layout.values():
        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue

            disliked_people = guest.get("dislikes", [])
            cannot_sit = guest.get("cannot_sit_with", [])

            for other_name in guests:
                if other_name == guest_name:
                    continue
                if other_name in disliked_people:
                    tension -= 10
                if other_name in cannot_sit:
                    tension -= 20

    return tension


def _calculate_gossip(player_layout, guests_dict):
    gossip = 0

    for guests in player_layout.values():
        ex_count = 0
        drama_count = 0

        for guest_name in guests:
            guest = guests_dict.get(guest_name)
            if not guest:
                continue

            if guest.get("type") == "ex":
                ex_count += 1

            if "drama" in guest.get("groups", []):
                drama_count += 1

        if ex_count >= 2:
            gossip -= 20
        elif ex_count == 1:
            gossip -= 5

        if drama_count >= 2:
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
            must_sit = guest.get("must_sit_with", [])

            for other_name in guests:
                if other_name != guest_name and other_name in cannot_sit:
                    violations.append(f"Hard constraint broken: {guest_name} and {other_name} at {table}")
                    score -= 50

            for required_name in must_sit:
                if required_name not in guests:
                    violations.append(f"Must-sit rule broken: {guest_name} is not seated with {required_name}")
                    score -= 30

    return score, violations
