import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from recommendation import df, get_recommendations, check_conflicts

# ----------------------------------------------------------------------------- helpers
category_mapping = {
    "moisturizer": "moisturiser", "cleanser": "cleanser",
    "serum": "serum", "toner": "toner",
    "eye cream": "eye cream", "mask": "mask"
}

# User-facing term -> INCI names that actually appear on ingredient lists.
INGREDIENT_SYNONYMS = {
    "vitamin c": ["ascorbic acid", "ascorbyl glucoside", "sodium ascorbyl phosphate",
                  "magnesium ascorbyl phosphate", "ascorbyl palmitate",
                  "tetrahexyldecyl ascorbate", "3-o-ethyl ascorbic acid"],
    "hyaluronic acid": ["hyaluronic acid", "sodium hyaluronate", "hydrolyzed hyaluronic acid",
                        "sodium acetylated hyaluronate", "potassium hyaluronate"],
    "ceramides": ["ceramide"],
    "niacinamide": ["niacinamide", "nicotinamide"],
    "retinol": ["retinol", "retinal", "retinaldehyde", "retinyl palmitate",
                "retinyl acetate", "hydroxypinacolone retinoate", "adapalene"],
    "centella": ["centella asiatica", "madecassoside", "asiaticoside",
                 "madecassic acid", "asiatic acid", "cica"],
    "salicylic acid": ["salicylic acid", "betaine salicylate", "willow bark"],
    "glycolic acid": ["glycolic acid", "sodium glycolate"],
    "lactic acid": ["lactic acid"],
    "zinc": ["zinc oxide", "zinc pca", "zinc gluconate", "zinc sulfate"],
}


def normalize_category(cat_str):
    return category_mapping.get(cat_str.lower().strip(), cat_str.lower().strip()) if cat_str else ""


def ingredient_present(term, ing_text):
    term = term.lower().strip()
    candidates = INGREDIENT_SYNONYMS.get(term, [term])
    return any(re.search(rf"\b{re.escape(c)}\b", ing_text) for c in candidates)


def expand_query(ingredients):
    out = []
    for i in ingredients:
        out.extend(INGREDIENT_SYNONYMS.get(i.lower().strip(), [i.lower()]))
    return list(dict.fromkeys(out))


# ----------------------------------------------------------------------------- systems
def baseline(q):
    """Raw ingredient vector baseline: comma-tokenized TF-IDF on clean_ingreds, nothing else."""
    query = ", ".join(q["ing"] + q["concerns"])
    return get_recommendations(user_query=query, product_type=normalize_category(q["type"]), top_n=4) or []


def multi_attribute(q, sensory_weight=0.3, top_n=4):
    """Ingredient sub-vector (synonym-expanded) + sensory sub-vector (scent/texture vs product name)."""
    user_query = " ".join(q["ing"] + q["concerns"])
    return get_recommendations(
        user_query=user_query,
        product_type=q["type"],
        desired_ingredients=q["ing"],
        skin_concerns=q["concerns"],
        texture_preference=q.get("texture"),
        sensory_weight=sensory_weight,
        top_n=top_n
    ) or []


SYSTEMS = {
    "Baseline (raw ingredient TF-IDF)": baseline,
    "Ingredient-only (+synonyms, no sensory)": lambda q: multi_attribute(q, sensory_weight=0.0),
    "Multi-attribute (ingredient + sensory)": lambda q: multi_attribute(q, sensory_weight=0.3),
}
BASE, ING_ONLY, FULL = list(SYSTEMS)


# ----------------------------------------------------------------------------- Part A metrics
def relevance_score(product, target_ing, target_type, texture):
    """3 = all ingredients + type + texture, 2 = all ingredients + type, 1 = ingredients or type, 0 = neither."""
    if not product or not isinstance(product, dict): return 0
    ing_text = str(product.get("clean_ingreds", "")).lower()
    type_text = str(product.get("product_type", "")).lower()
    name_text = str(product.get("product_name", "")).lower()

    m_ing = all(ingredient_present(i, ing_text) for i in target_ing)
    m_type = normalize_category(target_type) in type_text
    m_sens = (texture.lower() in name_text or texture.lower() in ing_text) if texture and texture != "any" else True

    if m_ing and m_type and m_sens: return 3
    if m_ing and m_type: return 2
    if m_ing or m_type: return 1
    return 0


def ndcg_at_k(retrieved_grades, pool_grades, k=4):
    """nDCG where the ideal ranking comes from the whole catalogue, not from the retrieved list."""
    disc = lambda n: 1 / np.log2(np.arange(2, n + 2))
    got = np.array([2 ** r - 1 for r in retrieved_grades[:k]], dtype=float)
    ideal = np.array([2 ** r - 1 for r in sorted(pool_grades, reverse=True)[:k]], dtype=float)
    idcg = (ideal * disc(len(ideal))).sum()
    return 0.0 if idcg == 0 else float((got * disc(len(got))).sum() / idcg)


def paired_bootstrap(diffs, n=10000, seed=0):
    """Mean of per-query differences with a 95% bootstrap confidence interval."""
    diffs = np.asarray(diffs, dtype=float)
    rng = np.random.default_rng(seed)
    means = rng.choice(diffs, size=(n, len(diffs)), replace=True).mean(axis=1)
    return diffs.mean(), np.percentile(means, [2.5, 97.5])


TEST_QUERIES = [
    {"id": 1, "ing": ["Retinol", "Glycolic Acid"], "concerns": ["Acne"], "type": "Serum", "scent": "unscented",
     "texture": "gel"},
    {"id": 2, "ing": ["Niacinamide", "Hyaluronic Acid"], "concerns": ["Dryness"], "type": "Moisturizer",
     "scent": "unscented", "texture": "cream"},
    {"id": 3, "ing": ["Salicylic Acid"], "concerns": ["Acne"], "type": "Cleanser", "scent": "unscented",
     "texture": "gel"},
    {"id": 4, "ing": ["Vitamin C"], "concerns": ["Hyperpigmentation"], "type": "Serum", "scent": "any",
     "texture": "lotion"},
    {"id": 5, "ing": ["Retinol", "Niacinamide"], "concerns": ["Fine Lines"], "type": "Serum", "scent": "unscented",
     "texture": "cream"},
    {"id": 6, "ing": ["Centella"], "concerns": ["Sensitive Skin"], "type": "Toner", "scent": "unscented",
     "texture": "any"},
    {"id": 7, "ing": ["Glycolic Acid", "Lactic Acid"], "concerns": ["Texture"], "type": "Serum", "scent": "any",
     "texture": "gel"},
    {"id": 8, "ing": ["Ceramides", "Hyaluronic Acid"], "concerns": ["Eczema"], "type": "Moisturizer",
     "scent": "unscented", "texture": "cream"},
    {"id": 9, "ing": ["Salicylic Acid", "Retinol"], "concerns": ["Breakouts"], "type": "Serum", "scent": "any",
     "texture": "gel"},
    {"id": 10, "ing": ["Zinc", "Niacinamide"], "concerns": ["Oil Control"], "type": "Serum", "scent": "unscented",
     "texture": "gel"},
    {"id": 12, "ing": ["Ceramides"], "concerns": ["Barrier Repair"], "type": "Moisturizer", "scent": "any",
     "texture": "balm"},
    {"id": 13, "ing": ["Centella", "Niacinamide"], "concerns": ["Redness"], "type": "Mask", "scent": "unscented",
     "texture": "any"},
]

CONFLICT_CASES = [
    (["Retinol", "Glycolic Acid"], True, "retinoid + AHA"),
    (["Retinol", "Salicylic Acid"], True, "retinoid + BHA"),
    (["Retinol", "Lactic Acid"], True, "retinoid + AHA"),
    (["Retinol", "Benzoyl Peroxide"], True, "retinoid + benzoyl peroxide"),
    (["Glycolic Acid", "Salicylic Acid"], True, "AHA + BHA (over-exfoliation)"),
    (["Niacinamide", "Hyaluronic Acid"], False, "compatible"),
    (["Niacinamide", "Retinol"], False, "compatible"),
    (["Ceramides", "Retinol"], False, "compatible"),
    (["Vitamin C", "Hyaluronic Acid"], False, "compatible"),
    (["Centella", "Niacinamide"], False, "compatible"),
    (["Zinc", "Niacinamide"], False, "compatible"),
    (["Salicylic Acid", "Niacinamide"], False, "compatible"),
    (["Ceramides", "Hyaluronic Acid"], False, "compatible"),
    (["Glycolic Acid", "Hyaluronic Acid"], False, "compatible"),
    (["Retinol"], False, "single ingredient"),
]

DISPUTED_CASES = [
    (["Vitamin C", "Retinol"]),
    (["Vitamin C", "Glycolic Acid"]),
    (["Vitamin C", "Salicylic Acid"]),
]

def evaluate_quality():
    per_query = {name: [] for name in SYSTEMS}
    pool_max = []
    records = df.to_dict("records")
    for q in TEST_QUERIES:
        pool = [relevance_score(r, q["ing"], q["type"], q["texture"]) for r in records]
        pool_max.append(max(pool))
        for name, fn in SYSTEMS.items():
            grades = [relevance_score(p, q["ing"], q["type"], q["texture"]) for p in fn(q)]
            per_query[name].append({"grades": grades, "ndcg": ndcg_at_k(grades, pool)})

    keep = [m >= 2 for m in pool_max]
    return per_query, pool_max, keep


if __name__ == "__main__":
    # ============================================================ PART A
    print("=" * 78)
    print("PART A: recommendation quality (grades: 3 = ingredients+type+texture, 2 = ingredients+type)")
    print("=" * 78)

    per_query, pool_max, keep = evaluate_quality()
    n_keep = sum(keep)
    print(f"{n_keep} of {len(TEST_QUERIES)} queries are scorable (the catalogue has a product that matches "
          f"all requested ingredients and the type); the rest are excluded.\n")

    print(f"{'QID':<5} {'best grade':>10} | " + " | ".join(f"{n.split(' (')[0]:<16}" for n in SYSTEMS))
    for i, q in enumerate(TEST_QUERIES):
        mark = "" if keep[i] else "  (excluded)"
        cells = " | ".join(f"{per_query[n][i]['ndcg']:<16.3f}" for n in SYSTEMS)
        print(f"Q{q['id']:<4} {pool_max[i]:>10} | {cells}{mark}")

    print("\nSummary over scorable queries")
    print(f"{'System':<42} {'nDCG@4':>8} {'P@4 (>=2)':>10} {'Mean grade':>11}")
    for name in SYSTEMS:
        rows = [r for r, k in zip(per_query[name], keep) if k]
        ndcg = np.mean([r["ndcg"] for r in rows])
        p4 = np.mean([np.mean([g >= 2 for g in r["grades"]]) for r in rows])
        mg = np.mean([np.mean(r["grades"]) for r in rows])
        print(f"{name:<42} {ndcg:>8.3f} {p4:>10.3f} {mg:>11.2f}")

    print("\nPaired comparison of nDCG@4 (per-query differences, 95% bootstrap CI)")
    for label, a, b in [("Multi-attribute vs baseline", FULL, BASE),
                        ("Multi-attribute vs ingredient-only (sensory effect)", FULL, ING_ONLY),
                        ("Ingredient-only vs baseline (synonym/search effect)", ING_ONLY, BASE)]:
        diffs = [per_query[a][i]["ndcg"] - per_query[b][i]["ndcg"] for i in range(len(TEST_QUERIES)) if keep[i]]
        mean, (lo, hi) = paired_bootstrap(diffs)
        w = sum(d > 1e-9 for d in diffs)
        l = sum(d < -1e-9 for d in diffs)
        t = len(diffs) - w - l
        print(f"  {label:<55} {mean:+.3f}  [{lo:+.3f}, {hi:+.3f}]  wins/ties/losses: {w}/{t}/{l}")

    # ============================================================ PART B
    print("\n" + "=" * 78)
    print("PART B: rule engine reliability on labelled ingredient combinations")
    print("=" * 78)
    tp = fp = fn = tn = 0
    misses, false_alarms = [], []
    print(f"{'Ingredients':<38} {'expected':>9} {'flagged':>8} {'#warn':>6}  result")
    for ings, expected, note in CONFLICT_CASES:
        warnings = check_conflicts(ings)
        flagged = bool(warnings)
        if expected and flagged:
            tp += 1; result = "TP"
        elif expected and not flagged:
            fn += 1; result = "FN (missed)"; misses.append((ings, note))
        elif not expected and flagged:
            fp += 1; result = "FP (false alarm)"; false_alarms.append((ings, note))
        else:
            tn += 1; result = "TN"
        print(f"{' + '.join(ings):<38} {str(expected):>9} {str(flagged):>8} {len(warnings):>6}  {result}")

    precision = tp / (tp + fp) if tp + fp else float("nan")
    recall = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else float("nan")
    acc = (tp + tn) / len(CONFLICT_CASES)
    print(f"\nConfusion matrix: TP={tp} FN={fn} FP={fp} TN={tn}")
    print(f"Precision={precision:.2f}  Recall={recall:.2f}  F1={f1:.2f}  Accuracy={acc:.2f}")
    if misses:
        print("Missed conflicts:", "; ".join(f"{' + '.join(i)} ({n})" for i, n in misses))
    if false_alarms:
        print("False alarms:", "; ".join(f"{' + '.join(i)} ({n})" for i, n in false_alarms))

    print("\nDisputed pairs (no ground truth, not scored):")
    for ings in DISPUTED_CASES:
        print(f"  {' + '.join(ings):<30} flagged by engine: {bool(check_conflicts(ings))}")
