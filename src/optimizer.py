"""
Optimization engine for wedding seating game.
Finds good seating arrangements automatically.
"""

def solve(level_data, guests_data):
    """
    Find a good seating arrangement.

    Args:
        level_data: dict with table_count, seats_per_table, vip_tables, and rules
        guests_data: list or dict of guests

    Returns:
        dict of table assignments
    """
    if isinstance(guests_data, dict):
        guests_list = guests_data
    else:
        guests_list = guests_data

    table_count = level_data.get("table_count", 3)
    seats_per_table = level_data.get("seats_per_table", 8)
    vip_tables = level_data.get("vip_tables", [])

    layout = _build_empty_tables(table_count)
    guest_names = _get_guest_names(guests_list)

    for guest_name in _sort_guests_for_placement(guest_names, guests_list):
        guest = _get_guest(guest_name, guests_list)
        best_table = _find_best_table(guest_name, guest, layout, guests_list, seats_per_table, vip_tables)
        if best_table:
            layout[best_table].append(guest_name)
        else:
            for table_name, guests in layout.items():
                if len(guests) < seats_per_table:
                    layout[table_name].append(guest_name)
                    break

    return layout


def _build_empty_tables(table_count):
    return {f"Table {i+1}": [] for i in range(table_count)}


def _get_guest_names(guests_data):
    if isinstance(guests_data, list):
        return [g["name"] for g in guests_data]
    return list(guests_data.keys())


def _get_guest(guest_name, guests_data):
    if isinstance(guests_data, list):
        for g in guests_data:
            if g["name"] == guest_name:
                return g
    else:
        return guests_data.get(guest_name)
    return None


def _sort_guests_for_placement(guest_names, guests_data):
    vips = []
    families = {}
    others = []

    for name in guest_names:
        guest = _get_guest(name, guests_data)
        if not guest:
            others.append(name)
            continue
        if guest.get("is_vip"):
            vips.append(name)
        else:
            family = guest.get("family", "other")
            families.setdefault(family, []).append(name)

    result = vips
    for family_list in families.values():
        result.extend(family_list)
    result.extend(others)
    return result


def _find_best_table(guest_name, guest, layout, guests_data, seats_per_table, vip_tables):
    best_score = float("-inf")
    best_table = None

    for table_name, table_guests in layout.items():
        if len(table_guests) >= seats_per_table:
            continue
        if guest.get("is_vip") and table_name not in vip_tables:
            continue
        score = _calculate_table_score(guest_name, guest, table_guests, guests_data)
        if score > best_score:
            best_score = score
            best_table = table_name

    return best_table


def _calculate_table_score(guest_name, guest, table_guests, guests_data):
    score = 0
    preferred = guest.get("preferred_with", [])
    for other_name in table_guests:
        if other_name in preferred:
            score += 20
    cannot_sit = guest.get("cannot_sit_with", [])
    for other_name in table_guests:
        if other_name in cannot_sit:
            score -= 100
    family = guest.get("family", "")
    if family:
        family_count = sum(
            1
            for g in table_guests
            if _get_guest(g, guests_data) and _get_guest(g, guests_data).get("family") == family
        )
        if family_count > 0:
            score += 15
    tags = guest.get("tags", [])
    table_tags = []
    for other_name in table_guests:
        other = _get_guest(other_name, guests_data)
        if other:
            table_tags.extend(other.get("tags", []))
    if "social" in tags and "quiet" in table_tags:
        score += 10
    if "quiet" in tags and "social" in table_tags:
        score += 10
    return score
