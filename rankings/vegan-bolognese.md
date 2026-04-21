# Vegan Bolognese Sauces

## How to use this file

Each product has two tables:

1. **Facts** — filled in once from the label/receipt (objective, not scored).
2. **Tasting scores** — one row per group member, scoring the subjective criteria 1–10.

Every member also sets **personal weights** (below) expressing how much each criterion matters to them. A per-member weighted score is then computed across all products, and the leaderboard is sorted by the group-average weighted score.

Add yourself as a column in the rater tables, and as a row in the personal-weights table. Leave a cell blank if you haven't tried a product yet.

## Criteria

| Criterion | Type | Scale / Unit | Notes |
|---|---|---|---|
| Flavor | subjective | 1 (bad) – 10 (excellent) | Your personal taste impression. |
| Sugar content | objective | g / 100 g | From nutrition label. Lower is better. |
| Protein content | objective | g / 100 g | From nutrition label. Higher is better. |
| Additives | objective | count + list | Count E-numbers, thickeners, flavorings, preservatives. Lower is better. |
| Cost | objective | € / 100 g | Normalize by jar weight: `price / (net_weight_g / 100)`. |

**Rater legend:** M1 = Member 1, M2 = Member 2, M3 = Member 3 — rename these to match your group.

## Personal weights

Each row is one group member. Weights are arbitrary positive numbers expressing the *relative* importance of each criterion (they don't have to sum to anything specific — they're normalized to sum to 1 per row before use). Leave at 1 if you're indifferent, push higher for things that matter more to you, lower for things you don't care about.

| Member | Flavor | Sugar | Protein | Additives | Cost |
|---|---|---|---|---|---|
| M1 | 1 | 1 | 1 | 1 | 1 |
| M2 | 1 | 1 | 1 | 1 | 1 |
| M3 | 1 | 1 | 1 | 1 | 1 |

## Scoring formula

For each criterion, every product is normalized to a 0–10 sub-score *relative to the other products in this file*, with the "better" direction accounted for:

- **Flavor** (higher = better): use the member's own flavor score directly (already 1–10).
- **Sugar, Additives, Cost** (lower = better): `sub = 10 * (max - x) / (max - min)`
- **Protein** (higher = better): `sub = 10 * (x - min) / (max - min)`

If `max == min` for a criterion (all products tied), give every product 5 for that criterion.

A member's **weighted score** for a product is then:

```
weighted = Σ (w_i / Σw) * sub_i
```

where `w_i` is that member's weight for criterion `i`. The **group score** is the average of the per-member weighted scores (skipping members who haven't rated the product's flavor yet).

Markdown can't compute this on its own — drop the data into a spreadsheet (or the Python helper we can add later) when you want fresh numbers.

---

## Products

### Template (copy this block for each new product)

**Brand / Name:** _TBD_
**Where bought:** _TBD_
**Jar size:** _TBD g_
**Price:** _TBD €_
**Link / notes:** _TBD_

**Facts**

| Sugar (g/100g) | Protein (g/100g) | Additives (count) | Additives (list) | Cost (€/100g) |
|---|---|---|---|---|
| - | - | - | - | - |

**Tasting scores (flavor, 1–10)**

| M1 | M2 | M3 | Avg |
|---|---|---|---|
| - | - | - | - |

**Comments:**
- _free-form notes from any member_

---

<!-- Add products below this line -->

### 1. _First product here_

**Brand / Name:**
**Where bought:**
**Jar size:**
**Price:**
**Link / notes:**

**Facts**

| Sugar (g/100g) | Protein (g/100g) | Additives (count) | Additives (list) | Cost (€/100g) |
|---|---|---|---|---|
| | | | | |

**Tasting scores (flavor, 1–10)**

| M1 | M2 | M3 | Avg |
|---|---|---|---|
| | | | |

**Comments:**
-

---

## Leaderboard

Sort by **Group weighted** for the overall ranking. The per-member columns show each member's personal weighted score using their own weights — useful for seeing who disagrees and why.

| # | Product | Avg flavor | Sugar | Protein | Additives | Cost | M1 weighted | M2 weighted | M3 weighted | **Group weighted** |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | | |
| 2 | | | | | | | | | | |
| 3 | | | | | | | | | | |
