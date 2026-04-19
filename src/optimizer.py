"""
Optimization engine for wedding seating assignment problem.

Mathematical Model (Binary Integer Programming solved via Simulated Annealing):

Sets:
    I  = set of guests
    T  = set of tables
    VIP, BVIP, EXIT, DANCE ⊆ I   (special guest subsets)
    T^vip, T^bridge, T^exit, T^dance ⊆ T  (special table subsets)

Parameters:
    cap_t       = capacity of table t
    a_it        = score of assigning guest i to table t
    b_ij        = compatibility score between guests i and j
    conflict_ij = 1 if guests i,j cannot sit together
    must_ij     = 1 if guests i,j must sit together

Decision Variables:
    x_it  ∈ {0,1}  — guest i assigned to table t
    y_ijt ∈ {0,1}  — guests i,j sit together at table t

Objective:
    max Z = ΣΣ a_it·x_it + ΣΣ b_ij·y_ijt

Constraints:
    1. Each guest assigned to exactly one table
    2. Table capacity not exceeded
    3. Conflicting guests not at same table
    4. Must-sit guests at same table
    5. Special seating preferences (VIP, bridge, exit, dance)
"""

import random
import copy
import math

# ─── Table zone properties per level ──────────────────────────────────────────
# Derived from renderer.py LEVEL_TABLE_LAYOUTS and ZONES positions
# EXIT zone center ≈ (100, 635), DANCE zone center ≈ (640, 640)

_TABLE_ZONES = {
    1: {
        "Table 1": {"zone": "vip_bride", "near_exit": False, "near_dance": True},
        "Table 2": {"zone": "vip_groom", "near_exit": False, "near_dance": False},
        "Table 3": {"zone": "general",   "near_exit": True,  "near_dance": True},
    },
    2: {
        "Table 1": {"zone": "vip_bride", "near_exit": False, "near_dance": False},
        "Table 2": {"zone": "vip_groom", "near_exit": False, "near_dance": False},
        "Table 3": {"zone": "general",   "near_exit": True,  "near_dance": False},
        "Table 4": {"zone": "general",   "near_exit": False, "near_dance": True},
        "Table 5": {"zone": "general",   "near_exit": False, "near_dance": False},
    },
    3: {
        "Table 1": {"zone": "vip_bride", "near_exit": False, "near_dance": False},
        "Table 2": {"zone": "vip_groom", "near_exit": False, "near_dance": False},
        "Table 3": {"zone": "general",   "near_exit": True,  "near_dance": False},
        "Table 4": {"zone": "general",   "near_exit": False, "near_dance": False},
        "Table 5": {"zone": "general",   "near_exit": False, "near_dance": False},
        "Table 6": {"zone": "general",   "near_exit": False, "near_dance": False},
        "Table 7": {"zone": "general",   "near_exit": False, "near_dance": True},
    },
}


def _prepare_guests(guests_data):
    """Normalize guest data: resolve id-based refs to names."""
    if isinstance(guests_data, list):
        guests = list(guests_data)
    else:
        guests = list(guests_data.values())
    id_to_name = {g["id"]: g["name"] for g in guests}
    by_name = {}
    for g in guests:
        resolved = dict(g)
        for field in ("likes", "dislikes", "must_sit_with", "cannot_sit_with"):
            resolved[field] = [id_to_name.get(ref, ref) for ref in resolved.get(field, [])]
        by_name[g["name"]] = resolved
    return guests, by_name, id_to_name


def _guest_table_score(guest, table_name, table_props):
    """Calculate a_it: score of assigning guest i to table t based on special tags."""
    score = 0
    tags = guest.get("special_tags", [])
    zone = table_props.get("zone", "general")

    # VIP placement: bride_vip guests should be at vip_bride tables
    if "bride_vip" in tags:
        if zone == "vip_bride":
            score += 15
        elif zone != "general":
            score -= 8
    if "groom_vip" in tags:
        if zone == "vip_groom":
            score += 15
        elif zone != "general":
            score -= 8

    # VIP type guests should be at any VIP table
    guest_type = guest.get("type", "")
    groups = guest.get("groups", [])
    is_vip = guest_type == "vip" or "vip" in groups
    if is_vip:
        if zone in ("vip_bride", "vip_groom"):
            score += 10
        else:
            score -= 5

    # Exit preference
    if "near_exit" in tags:
        if table_props.get("near_exit"):
            score += 10
        else:
            score -= 3

    # Dance floor preference
    if "near_dance_floor" in tags:
        if table_props.get("near_dance"):
            score += 10
        else:
            score -= 3

    return score


def _pairwise_score(g1, g2):
    """Calculate b_ij: compatibility score between two guests."""
    score = 0

    # Likes (symmetric check)
    if g2["name"] in g1.get("likes", []):
        score += 10
    if g1["name"] in g2.get("likes", []):
        score += 10

    # Must sit with (very strong)
    if g2["name"] in g1.get("must_sit_with", []):
        score += 20
    if g1["name"] in g2.get("must_sit_with", []):
        score += 20

    # Dislikes
    if g2["name"] in g1.get("dislikes", []):
        score -= 12
    if g1["name"] in g2.get("dislikes", []):
        score -= 12

    # Same family/group bonus
    g1_groups = set(g1.get("groups", []))
    g2_groups = set(g2.get("groups", []))
    shared = g1_groups & g2_groups
    for grp in shared:
        if "family" in grp:
            score += 5
        elif grp not in ("drama", "vip"):
            score += 3

    # Both exes at same table is bad gossip
    if g1.get("type") == "ex" and g2.get("type") == "ex":
        score -= 15

    # Drama group clustering is bad
    if "drama" in g1_groups and "drama" in g2_groups:
        score -= 8

    return score


def _hard_conflict(g1, g2):
    """Check if conflict_ij = 1 (cannot sit together)."""
    if g2["name"] in g1.get("cannot_sit_with", []):
        return True
    if g1["name"] in g2.get("cannot_sit_with", []):
        return True
    return False


def _must_together(g1, g2):
    """Check if must_ij = 1 (must sit together)."""
    if g2["name"] in g1.get("must_sit_with", []):
        return True
    if g1["name"] in g2.get("must_sit_with", []):
        return True
    return False


# ─── Solution Evaluation ──────────────────────────────────────────────────────

def _evaluate_solution(assignment, by_name, table_names, table_zones):
    """
    Evaluate the full objective function:
    Z = Σ a_it·x_it + Σ b_ij·y_ijt − penalties
    """
    score = 0.0

    # Build tables from assignment
    tables = {t: [] for t in table_names}
    for guest_name, table in assignment.items():
        tables[table].append(guest_name)

    # a_it: guest-to-table preference scores
    for guest_name, table in assignment.items():
        guest = by_name[guest_name]
        props = table_zones.get(table, {})
        score += _guest_table_score(guest, table, props)

    # b_ij: pairwise compatibility for guests at the same table
    for table, guests in tables.items():
        for i in range(len(guests)):
            g1 = by_name[guests[i]]
            for j in range(i + 1, len(guests)):
                g2 = by_name[guests[j]]
                score += _pairwise_score(g1, g2)

    # Hard constraint penalties
    for table, guests in tables.items():
        for i in range(len(guests)):
            g1 = by_name[guests[i]]
            for j in range(i + 1, len(guests)):
                g2 = by_name[guests[j]]
                if _hard_conflict(g1, g2):
                    score -= 500  # Very heavy penalty

    # Must-sit-together penalty
    for guest_name, guest in by_name.items():
        for must_name in guest.get("must_sit_with", []):
            if must_name in assignment:
                if assignment[guest_name] != assignment[must_name]:
                    score -= 200  # Heavy penalty

    # Bride-groom family mix bonus (entertainment)
    for table, guests in tables.items():
        bride_side = groom_side = 0
        for gn in guests:
            g = by_name[gn]
            groups = g.get("groups", [])
            if any("bride" in gr for gr in groups):
                bride_side += 1
            if any("groom" in gr for gr in groups):
                groom_side += 1
        if bride_side > 0 and groom_side > 0:
            score += 6

    # Table fill bonus (prefer balanced tables)
    guest_counts = [len(guests) for guests in tables.values()]
    if guest_counts:
        avg = sum(guest_counts) / len(guest_counts)
        variance = sum((c - avg) ** 2 for c in guest_counts) / len(guest_counts)
        score -= variance * 2  # Penalize uneven distribution

    return score


# ─── Greedy Initial Solution ──────────────────────────────────────────────────

def _greedy_initial(guest_names, by_name, table_names, capacity, table_zones):
    """Build an initial feasible solution using greedy assignment."""
    assignment = {}
    table_counts = {t: 0 for t in table_names}

    # Sort: must_sit_with pairs first, then VIP, then constrained guests, then rest
    def priority(name):
        g = by_name[name]
        p = 0
        if g.get("must_sit_with"):
            p -= 100
        if g.get("type") == "vip" or "vip" in g.get("groups", []):
            p -= 50
        if g.get("cannot_sit_with"):
            p -= 20
        if g.get("special_tags"):
            p -= 10
        return p

    sorted_guests = sorted(guest_names, key=priority)

    for guest_name in sorted_guests:
        guest = by_name[guest_name]
        best_table = None
        best_score = float("-inf")

        for table in table_names:
            if table_counts[table] >= capacity:
                continue

            # Check hard conflicts with already-assigned guests at this table
            conflict = False
            for other_name, other_table in assignment.items():
                if other_table == table:
                    if _hard_conflict(guest, by_name[other_name]):
                        conflict = True
                        break
            if conflict:
                continue

            # Score this assignment
            props = table_zones.get(table, {})
            s = _guest_table_score(guest, table, props)

            # Bonus for being with must_sit partners
            for must_name in guest.get("must_sit_with", []):
                if assignment.get(must_name) == table:
                    s += 50

            # Bonus for being with liked guests
            for other_name, other_table in assignment.items():
                if other_table == table:
                    s += _pairwise_score(guest, by_name[other_name]) * 0.5

            if s > best_score:
                best_score = s
                best_table = table

        if best_table is None:
            # Fallback: put in any table with space
            for table in table_names:
                if table_counts[table] < capacity:
                    best_table = table
                    break

        if best_table:
            assignment[guest_name] = best_table
            table_counts[best_table] += 1

    return assignment


# ─── Simulated Annealing ─────────────────────────────────────────────────────

def _neighbor(assignment, guest_names, table_names, capacity):
    """Generate a neighbor solution by swapping two guests or moving one."""
    new_assign = dict(assignment)
    table_counts = {t: 0 for t in table_names}
    for t in new_assign.values():
        table_counts[t] += 1

    move_type = random.random()

    if move_type < 0.6 and len(guest_names) >= 2:
        # Swap two guests between different tables
        g1, g2 = random.sample(guest_names, 2)
        if new_assign[g1] != new_assign[g2]:
            new_assign[g1], new_assign[g2] = new_assign[g2], new_assign[g1]
    else:
        # Move one guest to a different table
        g = random.choice(guest_names)
        old_table = new_assign[g]
        candidates = [t for t in table_names
                      if t != old_table and table_counts[t] < capacity]
        if candidates:
            new_assign[g] = random.choice(candidates)

    return new_assign


def solve(level_data, guests_data, level_num=1):
    """
    Find an optimal seating arrangement using simulated annealing.

    Args:
        level_data: dict with table_count, seats_per_table, etc.
        guests_data: list of guest dicts
        level_num: which level (1, 2, or 3) for table zone info

    Returns:
        dict like {"Table 1": ["Guest A", "Guest B"], ...}
    """
    guests, by_name, id_to_name = _prepare_guests(guests_data)
    guest_names = [g["name"] for g in guests]

    table_count = level_data.get("table_count", 3)
    capacity = level_data.get("seats_per_table", 5)
    table_names = [f"Table {i+1}" for i in range(table_count)]
    table_zones = _TABLE_ZONES.get(level_num, {})

    # --- Phase 1: Greedy initial solution ---
    assignment = _greedy_initial(guest_names, by_name, table_names, capacity, table_zones)

    # --- Phase 2: Simulated Annealing ---
    current_score = _evaluate_solution(assignment, by_name, table_names, table_zones)
    best_assignment = dict(assignment)
    best_score = current_score

    # SA parameters — tuned for problem sizes 15–35 guests
    T = 100.0        # Initial temperature
    T_min = 0.1      # Minimum temperature
    alpha = 0.995    # Cooling rate
    iterations_per_temp = 80

    while T > T_min:
        for _ in range(iterations_per_temp):
            new_assignment = _neighbor(assignment, guest_names, table_names, capacity)
            new_score = _evaluate_solution(new_assignment, by_name, table_names, table_zones)

            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / T):
                assignment = new_assignment
                current_score = new_score

                if current_score > best_score:
                    best_score = current_score
                    best_assignment = dict(assignment)

        T *= alpha

    # --- Phase 3: Final hill-climbing polish ---
    for _ in range(2000):
        new_assignment = _neighbor(best_assignment, guest_names, table_names, capacity)
        new_score = _evaluate_solution(new_assignment, by_name, table_names, table_zones)
        if new_score > best_score:
            best_assignment = new_assignment
            best_score = new_score

    # Convert assignment dict to layout format
    layout = {t: [] for t in table_names}
    for guest_name, table in best_assignment.items():
        layout[table].append(guest_name)

    return layout
