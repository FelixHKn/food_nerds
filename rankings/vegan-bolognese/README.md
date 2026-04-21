# Vegan Bolognese Sauces

## Data files

| File | One row per | Fields |
|---|---|---|
| `products.csv` | product | `id, brand, name, jar_size_g, price_eur, sugar_g_100g, protein_g_100g, additive_count, additives, notes` |
| `tastings.csv` | (product, member) tasting | `product_id, member, flavor, comment` — multiple rows per product are expected (one per member, or several from the same member over time) |
| `weights.csv` | member | `member, flavor, sugar, protein, additives, cost` — personal importance weights (any positive numbers; auto-normalized per row) |

`product_id` in `tastings.csv` and `member` in `weights.csv` / `tastings.csv` must match exactly. Pick short stable IDs for products (e.g. `rapunzel-bolognese`, `alnatura-classic`).

## Criteria

| Criterion | Source | Direction | Notes |
|---|---|---|---|
| Flavor | `tastings.csv` (subjective) | higher = better | 1 (bad) – 10 (excellent) per member. |
| Sugar | `products.csv` (label) | lower = better | g / 100 g. |
| Protein | `products.csv` (label) | higher = better | g / 100 g. |
| Additives | `products.csv` (label) | lower = better | Count E-numbers, thickeners, flavorings, preservatives in `additive_count`; list them in `additives`. |
| Cost | computed | lower = better | `price_eur / (jar_size_g / 100)` → €/100 g. |

## Scoring formula

For each of sugar/protein/additives/cost, every product is normalized to a 0–10 sub-score *relative to the other products in this file*:

- Higher-is-better: `sub = 10 * (x - min) / (max - min)`
- Lower-is-better: `sub = 10 * (max - x) / (max - min)`
- If `max == min` (all tied on that criterion), every product gets 5.

Flavor is already 0–10 and per-member, so it's used directly.

A member's **weighted score** for a product is:

```
weighted = Σ (w_i / Σw) * sub_i
```

where `w_i` is that member's weight for criterion `i` (from `weights.csv`). The **group score** averages the per-member weighted scores, skipping members who haven't rated that product's flavor yet.

## Running the leaderboard

From the repo root:

```
python food_nerds/score.py food_nerds/rankings/vegan-bolognese
```

The script prints a sorted markdown leaderboard to stdout; redirect it into a file or paste it into a summary if you want a snapshot.

## Adding yourself / a new product

- **New member:** add a row to `weights.csv` (any ID, e.g. your first name). Then start adding rows to `tastings.csv`.
- **New product:** add a row to `products.csv` with a new `id`. Tastings can trickle in afterwards.
- **New tasting:** append a row to `tastings.csv`. It's fine to leave `flavor` blank if you only want to log a comment.
