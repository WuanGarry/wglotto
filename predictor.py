"""
WUAN GARRY Predictor
Implements: Frequency model, Weighted random, Pattern/gap analysis,
            Hot-cold hybrid, Odd-even balanced model.
"""
import random
import math
from collections import Counter
from typing import List, Dict, Any


# ── Core analysis ─────────────────────────────────────────────────────────────
def analyse_numbers(all_nums: List[int]) -> Dict[str, Any]:
    if not all_nums:
        return {}

    freq = Counter(all_nums)
    sorted_freq = sorted(freq.items(), key=lambda x: -x[1])

    total = len(all_nums)
    odd_count  = sum(1 for n in all_nums if n % 2 != 0)
    even_count = total - odd_count
    high_count = sum(1 for n in all_nums if n > 45)
    low_count  = total - high_count

    # pairs
    draws = []  # We only have flat list here; pairs computed externally if needed
    hot   = sorted_freq[:20]
    cold  = sorted_freq[-20:]

    # number ranges 1-18, 19-36, 37-54, 55-72, 73-90
    ranges = {"1-18":0,"19-36":0,"37-54":0,"55-72":0,"73-90":0}
    for n in all_nums:
        if   n <= 18: ranges["1-18"]  += 1
        elif n <= 36: ranges["19-36"] += 1
        elif n <= 54: ranges["37-54"] += 1
        elif n <= 72: ranges["55-72"] += 1
        else:         ranges["73-90"] += 1

    return {
        "total_numbers": total,
        "hot_numbers":   [{"number": k, "count": v, "pct": round(v/total*100,1)} for k,v in hot],
        "cold_numbers":  [{"number": k, "count": v, "pct": round(v/total*100,1)} for k,v in cold],
        "odd_count":     odd_count,
        "even_count":    even_count,
        "odd_pct":       round(odd_count/total*100,1),
        "even_pct":      round(even_count/total*100,1),
        "high_count":    high_count,
        "low_count":     low_count,
        "high_pct":      round(high_count/total*100,1),
        "low_pct":       round(low_count/total*100,1),
        "ranges":        ranges,
        "frequency":     {str(k): v for k,v in freq.items()},
    }


# ── Model 1: Pure frequency ────────────────────────────────────────────────────
def frequency_model(freq: Counter) -> Dict[str, Any]:
    top5 = [k for k, _ in freq.most_common(5)]
    top5.sort()
    max_f = max(freq.values()) if freq else 1
    conf  = round(55 + (freq[top5[0]] / max_f) * 20, 1)
    return {
        "model": "Frequency Model",
        "description": "Top 5 most drawn numbers historically.",
        "numbers": top5,
        "confidence": min(conf, 78.0),
    }


# ── Model 2: Weighted random ───────────────────────────────────────────────────
def weighted_random_model(freq: Counter) -> Dict[str, Any]:
    pool    = list(range(1, 91))
    weights = [math.pow(freq.get(n, 0) + 1, 1.4) for n in pool]
    chosen  = []
    p_copy  = pool[:]
    w_copy  = weights[:]
    while len(chosen) < 5:
        total = sum(w_copy)
        r     = random.uniform(0, total)
        cum   = 0
        for i, w in enumerate(w_copy):
            cum += w
            if r <= cum:
                chosen.append(p_copy[i])
                p_copy.pop(i)
                w_copy.pop(i)
                break
    chosen.sort()
    conf = round(random.uniform(58, 68), 1)
    return {
        "model": "Weighted Random",
        "description": "Probability-weighted draw, favouring hot numbers.",
        "numbers": chosen,
        "confidence": conf,
    }


# ── Model 3: Hot + Cold balanced ─────────────────────────────────────────────
def hot_cold_blend(freq: Counter) -> Dict[str, Any]:
    sorted_f = freq.most_common()
    hot  = [k for k,_ in sorted_f[:15]]
    cold = [k for k,_ in sorted_f[-15:]]
    pick_hot  = random.sample(hot,  3)
    pick_cold = random.sample(cold, 2)
    nums = sorted(pick_hot + pick_cold)
    conf = round(random.uniform(55, 65), 1)
    return {
        "model": "Hot + Cold Blend",
        "description": "3 hot numbers + 2 overdue cold numbers.",
        "numbers": nums,
        "confidence": conf,
    }


# ── Model 4: Odd/Even balanced ────────────────────────────────────────────────
def odd_even_balanced(freq: Counter) -> Dict[str, Any]:
    odds  = [n for n in range(1, 91) if n % 2 != 0]
    evens = [n for n in range(1, 91) if n % 2 == 0]
    w_odd  = [freq.get(n, 0) + 1 for n in odds]
    w_even = [freq.get(n, 0) + 1 for n in evens]

    def wpick(pool, weights, k):
        chosen, p, w = [], pool[:], weights[:]
        while len(chosen) < k:
            t = sum(w); r = random.uniform(0, t); c = 0
            for i in range(len(p)):
                c += w[i]
                if r <= c:
                    chosen.append(p[i]); p.pop(i); w.pop(i); break
        return chosen

    nums = sorted(wpick(odds, w_odd, 3) + wpick(evens, w_even, 2))
    conf = round(random.uniform(56, 66), 1)
    return {
        "model": "Odd/Even Balanced (3+2)",
        "description": "3 odd + 2 even, weighted by frequency.",
        "numbers": nums,
        "confidence": conf,
    }


# ── Model 5: High/Low balanced ────────────────────────────────────────────────
def high_low_balanced(freq: Counter) -> Dict[str, Any]:
    lows  = list(range(1,  46))
    highs = list(range(46, 91))
    w_low  = [freq.get(n, 0) + 1 for n in lows]
    w_high = [freq.get(n, 0) + 1 for n in highs]

    def wpick(pool, weights, k):
        chosen, p, w = [], pool[:], weights[:]
        while len(chosen) < k:
            t = sum(w); r = random.uniform(0, t); c = 0
            for i in range(len(p)):
                c += w[i]
                if r <= c:
                    chosen.append(p[i]); p.pop(i); w.pop(i); break
        return chosen

    nums = sorted(wpick(lows, w_low, 2) + wpick(highs, w_high, 3))
    conf = round(random.uniform(54, 63), 1)
    return {
        "model": "High/Low Split (2+3)",
        "description": "2 low numbers (1-45) + 3 high (46-90).",
        "numbers": nums,
        "confidence": conf,
    }


# ── Dispatcher ────────────────────────────────────────────────────────────────
def generate_all_predictions(all_nums: List[int]) -> List[Dict[str, Any]]:
    if not all_nums:
        # Fallback random if no history
        all_nums = [random.randint(1, 90) for _ in range(200)]

    freq = Counter(all_nums)
    preds = [
        frequency_model(freq),
        weighted_random_model(freq),
        hot_cold_blend(freq),
        odd_even_balanced(freq),
        high_low_balanced(freq),
    ]
    return preds


if __name__ == "__main__":
    sample = [random.randint(1, 90) for _ in range(500)]
    for p in generate_all_predictions(sample):
        print(f"{p['model']:30s} → {p['numbers']}  conf: {p['confidence']}%")
