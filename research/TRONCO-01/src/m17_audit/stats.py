"""Stdlib statistics for the leakage audit: association tests, classifier, power."""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from itertools import combinations


# ---------------------------------------------------------------- chi-square survival function

def _gser(a, x):
    ap, s = a, 1.0 / a
    d = s
    for _ in range(2000):
        ap += 1
        d *= x / ap
        s += d
        if abs(d) < abs(s) * 1e-15:
            break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gcf(a, x):
    tiny = 1e-300
    b = x + 1 - a
    c = 1 / tiny
    d = 1 / b
    h = d
    for i in range(1, 2000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_sf(x: float, df: int) -> float:
    if x <= 0 or df <= 0:
        return 1.0
    a, half = df / 2.0, x / 2.0
    return max(0.0, min(1.0, 1 - _gser(a, half))) if half < a + 1 else max(0.0, min(1.0, _gcf(a, half)))


# ---------------------------------------------------------------- binning and tests

def quantile_bins(values, max_bins=4):
    """Pooled (category-blind) bins for a numeric feature; returns a function value -> label."""
    distinct = sorted(set(values))
    if len(distinct) <= max_bins:
        return lambda v: v
    srt = sorted(values)
    cuts = sorted({srt[int(len(srt) * k / max_bins)] for k in range(1, max_bins)})
    return lambda v: sum(v >= c for c in cuts)


def _merge_rare(table, min_total):
    """Merge feature levels whose total count is below min_total into one level."""
    totals = {lvl: sum(row.values()) for lvl, row in table.items()}
    rare = [lvl for lvl, t in totals.items() if t < min_total]
    if len(rare) < 2 and not (rare and len(table) > 2):
        keep = dict(table)
    else:
        keep = {l: r for l, r in table.items() if l not in rare}
        merged = Counter()
        for l in rare:
            merged.update(table[l])
        keep[("__rare__",)] = dict(merged)
    return keep


def association(feature, labels):
    """Chi-square test of independence between a categorical feature and the labels.

    Returns dict(p, cramers_v, chi2, df, n, testable). Rare levels are merged so that
    every expected cell count is at least 5; if fewer than two levels remain the
    feature is reported as untestable (p = 1).
    """
    n = len(labels)
    cats = Counter(labels)
    table = defaultdict(Counter)
    for f, y in zip(feature, labels):
        table[f][y] += 1
    p_min = min(cats.values()) / n
    table = _merge_rare(table, math.ceil(5 / p_min))
    if len(table) < 2 or len(cats) < 2:
        return {"p": 1.0, "cramers_v": 0.0, "chi2": 0.0, "df": 0, "n": n, "testable": False}
    chi2 = 0.0
    for lvl, row in table.items():
        tot = sum(row.values())
        for y, cy in cats.items():
            exp = tot * cy / n
            chi2 += (row.get(y, 0) - exp) ** 2 / exp
    df = (len(table) - 1) * (len(cats) - 1)
    v = math.sqrt(chi2 / (n * min(len(table) - 1, len(cats) - 1)))
    return {"p": chi2_sf(chi2, df), "cramers_v": v, "chi2": chi2, "df": df, "n": n, "testable": True}


def holm(pvals: dict, alpha=0.05):
    """Holm step-down. Returns {name: (adjusted_p, rejected)}."""
    order = sorted(pvals, key=lambda k: pvals[k])
    m = len(order)
    out, running = {}, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (m - i) * pvals[k]))
        out[k] = (running, running <= alpha)
    return out


# ---------------------------------------------------------------- classifier

def wilson(successes, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


def naive_bayes_cv(rows, labels, folds=5):
    """Multinomial naive Bayes on categorical features, deterministic stratified k-fold."""
    n = len(labels)
    by_label = defaultdict(list)
    for i, y in enumerate(labels):
        by_label[y].append(i)
    fold_of = {}
    for y, idx in sorted(by_label.items(), key=lambda kv: str(kv[0])):
        for j, i in enumerate(idx):
            fold_of[i] = j % folds
    classes = sorted(by_label, key=str)
    names = sorted(rows[0])
    correct = 0
    for f in range(folds):
        train = [i for i in range(n) if fold_of[i] != f]
        test = [i for i in range(n) if fold_of[i] == f]
        prior = Counter(labels[i] for i in train)
        counts = {(y, k): Counter() for y in classes for k in names}
        levels = {k: set() for k in names}
        for i in train:
            for k in names:
                counts[(labels[i], k)][rows[i][k]] += 1
                levels[k].add(rows[i][k])
        for i in test:
            best, best_score = None, -1e300
            for y in classes:
                score = math.log(prior[y] / len(train))
                for k in names:
                    c = counts[(y, k)]
                    score += math.log((c[rows[i][k]] + 1) / (prior[y] + len(levels[k]) + 1))
                if score > best_score:
                    best, best_score = y, score
            correct += best == labels[i]
    lo, hi = wilson(correct, n)
    return {"accuracy": correct / n, "ci95": [lo, hi], "n": n, "chance": 1 / len(classes)}


def pairwise_nb(rows, labels, folds=5):
    out = {}
    cats = sorted(set(labels))
    for a, b in combinations(cats, 2):
        idx = [i for i, y in enumerate(labels) if y in (a, b)]
        out[f"{a}|{b}"] = naive_bayes_cv([rows[i] for i in idx], [labels[i] for i in idx], folds)
    return out


# ---------------------------------------------------------------- power of the association pipeline

def detection_rate(n_per_class, classes, strength, n_tests, alpha=0.05, sims=200, seed=1, levels=5):
    """How often a planted leak is rejected by Holm over `n_tests` tests (worst case: it is the
    smallest p of all tests). The planted feature equals a class-specific value with probability
    `strength`, otherwise it is uniform over `levels`. The other tests contribute nothing here, so
    the rejection criterion is p <= alpha / n_tests (Holm's first step)."""
    rng = random.Random(seed)
    labels = [c for c in range(classes) for _ in range(n_per_class)]
    hits = 0
    for _ in range(sims):
        feat = [(y % levels) if rng.random() < strength else rng.randrange(levels) for y in labels]
        hits += association(feat, labels)["p"] <= alpha / n_tests
    return hits / sims
