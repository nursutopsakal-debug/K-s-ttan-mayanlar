"""
GAMSPy MIP solver for wedding seating optimization problem.

Mathematical Model:
    max Z = Σ_i Σ_t a_it·x_it + Σ_{i<j} Σ_t b_ij·y_ijt

    s.t.
    (1) Σ_t x_it = 1                    ∀i ∈ I        (assignment)
    (2) Σ_i x_it ≤ cap_t                ∀t ∈ T        (capacity)
    (3) x_it + x_jt ≤ 1                 ∀(i,j)∈CF, ∀t (conflicts)
    (4) x_it = x_jt                      ∀(i,j)∈MS, ∀t (must-sit)
    (5) y_ijt ≤ x_it                     ∀i<j, ∀t      (linearization)
        y_ijt ≤ x_jt                     ∀i<j, ∀t
        y_ijt ≥ x_it + x_jt - 1         ∀i<j, ∀t

    x_it ∈ {0,1}, y_ijt ∈ {0,1}

Called via subprocess: python gamspy_solver.py < input.json > output.json
Input:  {n_guests, n_tables, capacity, a_scores, b_scores, conflicts, musts}
Output: {status, solution} where solution maps "table_idx" -> [guest_indices]
"""
import sys
import json


def main():
    try:
        data = json.loads(sys.stdin.read())
        solution = solve_mip(data)
        json.dump({"status": "ok", "solution": solution}, sys.stdout)
    except Exception as e:
        json.dump({"status": "error", "message": str(e)}, sys.stdout)


def solve_mip(data):
    from gamspy import (
        Container, Set, Alias, Parameter, Variable,
        Equation, Model, Sense, Sum,
    )

    ng = data["n_guests"]
    nt = data["n_tables"]
    cap_val = data["capacity"]
    a_raw = data["a_scores"]       # [[guest_idx, table_idx, score], ...]
    b_raw = data["b_scores"]       # [[gi, gj, score], ...]  (gi < gj)
    cf_raw = data["conflicts"]     # [[gi, gj], ...]
    ms_raw = data["musts"]         # [[gi, gj], ...]

    gids = [f"g{k}" for k in range(ng)]
    tids = [f"t{k}" for k in range(nt)]

    m = Container()

    # ── Sets ──────────────────────────────────────────────────────────────
    i = Set(m, name="i", records=gids)
    t = Set(m, name="t", records=tids)
    j = Alias(m, name="j", alias_with=i)

    # Ordered pairs (i < j)
    pair_recs = [[f"g{a}", f"g{b}"] for a in range(ng) for b in range(a + 1, ng)]
    ij = Set(m, name="ij", domain=[i, j], records=pair_recs)

    # Conflict pairs
    has_cf = len(cf_raw) > 0
    if has_cf:
        cf = Set(m, name="cf", domain=[i, j],
                 records=[[f"g{c[0]}", f"g{c[1]}"] for c in cf_raw])

    # Must-sit pairs
    has_ms = len(ms_raw) > 0
    if has_ms:
        ms = Set(m, name="ms", domain=[i, j],
                 records=[[f"g{p[0]}", f"g{p[1]}"] for p in ms_raw])

    # ── Parameters ────────────────────────────────────────────────────────
    cap_p = Parameter(m, name="cap", domain=t,
                      records=[[tid, float(cap_val)] for tid in tids])

    a_recs = [[f"g{r[0]}", f"t{r[1]}", float(r[2])] for r in a_raw]
    a_p = Parameter(m, name="a", domain=[i, t],
                    records=a_recs if a_recs else None)

    b_recs = [[f"g{r[0]}", f"g{r[1]}", float(r[2])] for r in b_raw]
    b_p = Parameter(m, name="b", domain=[i, j],
                    records=b_recs if b_recs else None)

    # ── Variables ─────────────────────────────────────────────────────────
    x = Variable(m, name="x", type="binary", domain=[i, t])
    y = Variable(m, name="y", type="binary", domain=[i, j, t])
    z = Variable(m, name="z", type="free")

    # ── Objective ─────────────────────────────────────────────────────────
    # Z = Σ a_it·x_it + Σ b_ij·y_ijt
    obj_expr = Sum([i, t], a_p[i, t] * x[i, t])
    if b_recs:
        obj_expr = obj_expr + Sum([i, j, t], b_p[i, j] * y[i, j, t])

    defobj = Equation(m, name="defobj")
    defobj[...] = z == obj_expr

    # ── Constraints ───────────────────────────────────────────────────────

    # (1) Each guest assigned to exactly one table
    assign = Equation(m, name="assign", domain=i)
    assign[i] = Sum(t, x[i, t]) == 1

    # (2) Table capacity
    cap_eq = Equation(m, name="cap_eq", domain=t)
    cap_eq[t] = Sum(i, x[i, t]) <= cap_p[t]

    # (3) Conflicting guests cannot sit at the same table
    if has_cf:
        no_cf = Equation(m, name="no_cf", domain=[i, j, t])
        no_cf[i, j, t].where[cf[i, j]] = x[i, t] + x[j, t] <= 1

    # (4) Must-sit guests at the same table
    if has_ms:
        must_eq = Equation(m, name="must_eq", domain=[i, j, t])
        must_eq[i, j, t].where[ms[i, j]] = x[i, t] == x[j, t]

    # (5) Linearization of y_ijt = x_it · x_jt  (only for ordered pairs)
    lin1 = Equation(m, name="lin1", domain=[i, j, t])
    lin1[i, j, t].where[ij[i, j]] = y[i, j, t] <= x[i, t]

    lin2 = Equation(m, name="lin2", domain=[i, j, t])
    lin2[i, j, t].where[ij[i, j]] = y[i, j, t] <= x[j, t]

    lin3 = Equation(m, name="lin3", domain=[i, j, t])
    lin3[i, j, t].where[ij[i, j]] = y[i, j, t] >= x[i, t] + x[j, t] - 1

    # ── Solve ─────────────────────────────────────────────────────────────
    model = Model(
        m, name="wedding_seating",
        equations=m.getEquations(),
        problem="MIP",
        sense=Sense.MAX,
        objective=z,
    )
    model.solve()

    # ── Extract solution ──────────────────────────────────────────────────
    xr = x.records
    sol = {str(k): [] for k in range(nt)}

    if xr is not None:
        for _, row in xr.iterrows():
            if row["level"] > 0.5:
                gi = int(row["i"][1:])    # "g5" -> 5
                ti = int(row["t"][1:])    # "t2" -> 2
                sol[str(ti)].append(gi)

    return sol


if __name__ == "__main__":
    main()
