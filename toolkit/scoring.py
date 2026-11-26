"""Scoring: blends self-reported answers with measured evidence, applies weakest-link caps, builds the roadmap."""
import json, os
from . import scanner
QUESTIONS = json.load(open(os.path.join(os.path.dirname(__file__), "data", "questions.json"), encoding="utf-8"))
LEVELS = {1: "Ad hoc", 2: "Reactive", 3: "Defined", 4: "Managed", 5: "Optimized"}
ANS = {"yes": 1.0, "partial": 0.5, "no": 0.0}
EVIDENCE_WEIGHT = 0.6   # measured evidence outweighs opinion
def strict(p):
    """A control failing for 1 in 3 identities is not 'two-thirds mature'. 50% pass or worse scores 0; 100% scores 100."""
    return round(max(0.0, (p - 50.0) * 2), 1)

def level(p): return 1 if p < 20 else 2 if p < 40 else 3 if p < 60 else 4 if p < 80 else 5
def _w(rs, key): return sum(r[key] * r["w"] for r in rs) / sum(r["w"] for r in rs)

def assess(answers, inv):
    checks, rows = scanner.run(inv), []
    for q in QUESTIONS:
        s = ANS.get(answers.get(q["id"], "no"), 0.0) * 100
        m = strict(checks[q["check"]]["pct"]) if q["check"] else None
        sc = s if m is None else round((1 - EVIDENCE_WEIGHT) * s + EVIDENCE_WEIGHT * m, 1)
        rows.append(dict(q, self=s, measured=m, score=sc, gap=None if m is None else round(s - m, 1)))
    domains = []
    for name in dict.fromkeys(q["domain"] for q in QUESTIONS):
        rs = [r for r in rows if r["domain"] == name]; lk = [r for r in rs if r["measured"] is not None]
        sc = _w(rs, "score"); lv, cap = level(sc), None
        for r in rs:   # weakest-link: one failed critical control caps the whole domain (measured evidence wins over opinion)
            v = r["measured"] if r["measured"] is not None else r["score"]
            if r["w"] == 3 and v < 30 and lv > 2: lv, cap = 2, r["id"]
            elif r["w"] == 3 and v < 60 and lv > 3: lv, cap = 3, r["id"]
        domains.append({"name": name, "score": round(sc, 1), "level": lv, "capped_by": cap, "self_all": round(_w(rs, "self"), 1),
            "self_linked": round(_w(lk, "self"), 1) if lk else None, "measured": round(_w(lk, "measured"), 1) if lk else None,
            "gap": round(_w(lk, "self") - _w(lk, "measured"), 1) if lk else None})
    score = sum(d["score"] for d in domains) / len(domains)
    overall = min(level(score), min(d["level"] for d in domains) + 1)
    R, tot = inv["resources"], sum(r["cost"] for r in inv["resources"])
    unalloc = sum(r["cost"] for r in R if not (r["tags"].get("owner") and r["tags"].get("cost_center")))
    gaps = [d["gap"] for d in domains if d["gap"] is not None]
    summary = {"score": round(score, 1), "level": overall, "avg_gap": round(sum(gaps) / len(gaps), 1) if gaps else 0.0,
        "monthly_cost": round(tot), "unallocated_pct": round(100 * unalloc / tot, 1), "idle_waste_annual": checks["IDLE"]["waste_usd_month"] * 12,
        "public_buckets": checks["PUBLIC"]["n_findings"], "no_mfa": checks["MFA"]["n_findings"], "critical_no_backup": checks["BACKUP"]["n_findings"],
        "outside_region": checks["REGION"]["n_findings"], "weakest": sorted(domains, key=lambda d: d["score"])[:3] and [d["name"] for d in sorted(domains, key=lambda d: d["score"])[:3]],
        "biggest_gaps": [d["name"] for d in sorted([d for d in domains if d["gap"] is not None], key=lambda d: -d["gap"])[:3]]}
    road = []
    for r in rows:
        if r["score"] >= 80: continue
        impact = round(r["w"] * (100 - r["score"]) / 100, 2)
        road.append({"id": r["id"], "domain": r["domain"], "action": r["fix"], "impact": impact, "effort": r["e"], "priority": round(impact / r["e"], 2),
                     "horizon": "0-30 days" if r["e"] <= 2 else "30-90 days" if r["e"] == 3 else "90-180 days", "refs": r["refs"], "score": r["score"]})
    road.sort(key=lambda x: -x["priority"])
    return {"rows": rows, "domains": domains, "checks": checks, "summary": summary, "roadmap": road}
