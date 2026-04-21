"""Compute the weighted leaderboard for a food ranking category.

Usage:
    python food_nerds/score.py food_nerds/rankings/vegan-bolognese

Reads products.csv, tastings.csv, weights.csv from the given directory and
prints a markdown leaderboard sorted by the group-average weighted score.
Stdlib only — no third-party dependencies.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from statistics import mean

CRITERIA = [
    ("flavor",    +1),
    ("sugar",     -1),
    ("protein",   +1),
    ("additives", -1),
    ("cost",      -1),
]


def _strip_row(row: dict) -> dict:
    return {(k or "").strip(): (v or "").strip() for k, v in row.items()}


def load_products(path: Path) -> dict[str, dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = [_strip_row(r) for r in csv.DictReader(f)]
    return {r["id"]: r for r in rows if r.get("id")}


def load_tastings(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [_strip_row(r) for r in csv.DictReader(f) if (r.get("product_id") or "").strip()]


def load_weights(path: Path) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for raw in csv.DictReader(f):
            row = _strip_row(raw)
            member = row.get("member", "")
            if not member:
                continue
            w = {c: float(row[c]) for c, _ in CRITERIA}
            total = sum(w.values()) or 1.0
            out[member] = {k: v / total for k, v in w.items()}
    return out


def _equal_weights() -> dict[str, float]:
    n = len(CRITERIA)
    return {c: 1.0 / n for c, _ in CRITERIA}


def _as_float(row: dict, key: str) -> float | None:
    raw = row.get(key, "")
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def normalize(values: dict[str, float], direction: int) -> dict[str, float]:
    vmin = min(values.values())
    vmax = max(values.values())
    if vmax == vmin:
        return {k: 5.0 for k in values}
    if direction > 0:
        return {k: 10 * (v - vmin) / (vmax - vmin) for k, v in values.items()}
    return {k: 10 * (vmax - v) / (vmax - vmin) for k, v in values.items()}


def cost_per_100g(product: dict) -> float:
    return float(product["price_eur"]) / (float(product["jar_size_g"]) / 100.0)


def main(category_dir: str) -> int:
    d = Path(category_dir)
    products = load_products(d / "products.csv")
    tastings = load_tastings(d / "tastings.csv")
    weights = load_weights(d / "weights.csv")

    if not products:
        print(f"No products in {d / 'products.csv'} yet — add some rows and re-run.", file=sys.stderr)
        return 1

    sugar_sub    = normalize({pid: float(p["sugar_g_100g"])   for pid, p in products.items()}, -1)
    protein_sub  = normalize({pid: float(p["protein_g_100g"]) for pid, p in products.items()}, +1)
    additive_sub = normalize({pid: float(p["additive_count"]) for pid, p in products.items()}, -1)
    cost_sub     = normalize({pid: cost_per_100g(p)           for pid, p in products.items()}, -1)

    flavor_by_product: dict[str, list[float]] = {pid: [] for pid in products}
    flavor_by_pair: dict[tuple[str, str], list[float]] = {}
    seen_members: set[str] = set()
    for t in tastings:
        pid, member = t.get("product_id", ""), t.get("member", "")
        raw = t.get("flavor", "")
        if pid not in products or not member or not raw:
            continue
        try:
            score = float(raw)
        except ValueError:
            print(f"warning: non-numeric flavor '{raw}' for product {pid} by {member} — skipped", file=sys.stderr)
            continue
        flavor_by_pair.setdefault((pid, member), []).append(score)
        flavor_by_product[pid].append(score)
        seen_members.add(member)

    for m in sorted(seen_members - set(weights)):
        print(f"warning: member '{m}' has tastings but no row in weights.csv — using equal weights", file=sys.stderr)
        weights[m] = _equal_weights()

    members = sorted(weights)
    member_scores: dict[str, dict[str, float]] = {m: {} for m in members}
    for pid in products:
        for m in members:
            flav = flavor_by_pair.get((pid, m))
            if not flav:
                continue
            subs = {
                "flavor":    mean(flav),
                "sugar":     sugar_sub[pid],
                "protein":   protein_sub[pid],
                "additives": additive_sub[pid],
                "cost":      cost_sub[pid],
            }
            w = weights[m]
            member_scores[m][pid] = sum(w[c] * subs[c] for c, _ in CRITERIA)

    group: dict[str, float] = {}
    for pid in products:
        vals = [member_scores[m][pid] for m in members if pid in member_scores[m]]
        if vals:
            group[pid] = mean(vals)

    ranked = [(pid, group[pid]) for pid in sorted(group, key=lambda p: group[p], reverse=True)]
    unranked = [pid for pid in products if pid not in group]

    header = ["#", "Product", "Avg flavor", "Sugar", "Protein", "Additives", "Cost/100g"]
    header += list(members) + ["**Group**"]
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join(["---"] * len(header)) + "|")

    def row_for(i: str, pid: str, gscore: float | None) -> None:
        p = products[pid]
        flavs = flavor_by_product[pid]
        avg_flav = f"{mean(flavs):.1f}" if flavs else "-"
        row = [
            i,
            f"{p.get('brand', '').strip()} — {p.get('name', '').strip()}".strip(" —"),
            avg_flav,
            p["sugar_g_100g"],
            p["protein_g_100g"],
            p["additive_count"],
            f"{cost_per_100g(p):.2f}",
        ]
        for m in members:
            s = member_scores[m].get(pid)
            row.append(f"{s:.2f}" if s is not None else "-")
        row.append(f"**{gscore:.2f}**" if gscore is not None else "-")
        print("| " + " | ".join(row) + " |")

    for i, (pid, gscore) in enumerate(ranked, 1):
        row_for(str(i), pid, gscore)
    for pid in unranked:
        row_for("–", pid, None)

    if unranked:
        print(f"\n_{len(unranked)} product(s) have no tastings yet and are listed unranked at the bottom._")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "category",
        nargs="?",
        default="food_nerds/rankings/vegan-bolognese",
        help="Path to a category directory containing products.csv, tastings.csv, weights.csv",
    )
    args = parser.parse_args()
    sys.exit(main(args.category))
