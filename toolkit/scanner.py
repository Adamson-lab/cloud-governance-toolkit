"""Evidence scanner: turns a cloud inventory export into MEASURED control scores (0-100)."""
def _pct(good, total): return 100.0 if total == 0 else round(100.0 * good / total, 1)

def run(inv):
    R, iam, acc = inv["resources"], inv["iam"], inv["accounts"]
    allowed, out = set(inv["policy"]["allowed_regions"]), {}
    def add(cid, name, bad, total, msgs, waste=0.0):
        out[cid] = {"id": cid, "name": name, "pct": _pct(total - len(bad), total), "total": total, "n_findings": len(bad),
                    "findings": msgs[:6], "waste_usd_month": round(waste, 2)}
    bad = [r for r in R if not (r["tags"].get("owner") and r["tags"].get("cost_center"))]
    add("TAGS", "Resources with owner + cost-center tags", bad, len(R), [f"{r['id']} (${r['cost']:,.0f}/mo) missing owner/cost-center" for r in sorted(bad, key=lambda r: -r["cost"])])
    b = [r for r in R if r["type"] == "bucket"]; bad = [r for r in b if r["public"]]
    add("PUBLIC", "Storage buckets not publicly exposed", bad, len(b), [f"{r['id']} in {r['region']} is PUBLIC" for r in bad])
    st = [r for r in R if r["type"] in ("bucket", "disk", "db")]; bad = [r for r in st if not r["encrypted"]]
    add("ENCRYPT", "Data stores encrypted at rest", bad, len(st), [f"{r['id']} ({r['type']}) unencrypted" for r in bad])
    U = iam["users"]; msgs = (["ROOT account has no MFA"] if not iam["root_mfa"] else []) + [f"{u['name']} has no MFA" for u in U if not u["mfa"]]
    out_total = len(U) + 1; nbad = len([u for u in U if not u["mfa"]]) + (0 if iam["root_mfa"] else 1)
    out["MFA"] = {"id": "MFA", "name": "Identities (incl. root) with MFA", "pct": _pct(out_total - nbad, out_total), "total": out_total, "n_findings": nbad, "findings": msgs[:6], "waste_usd_month": 0}
    P = iam["policies"]; bad = [p for p in P if p["wildcard"]]
    add("WILDCARD", "Policies without wildcard admin", bad, len(P), [f"{p['name']} grants *:*" for p in bad])
    bad = [u for u in U if u["last_used_days"] > 90]
    add("STALE", "Identities active in last 90 days", bad, len(U), [f"{u['name']} idle {u['last_used_days']} days" for u in bad])
    bad = [r for r in R if r["region"] not in allowed]
    add("REGION", "Resources inside approved regions", bad, len(R), [f"{r['id']} in {r['region']} (not allowed)" for r in bad])
    comp = [r for r in R if r["type"] in ("vm", "k8s")]; bad = [r for r in comp if r["cpu_avg"] < 5]
    add("IDLE", "Compute not idle (CPU avg >= 5%)", bad, len(comp), [f"{r['id']} CPU {r['cpu_avg']}% costs ${r['cost']:,.0f}/mo" for r in sorted(bad, key=lambda r: -r["cost"])], sum(r["cost"] for r in bad))
    crit = [r for r in R if r["critical"]]; bad = [r for r in crit if not r["backup"]]
    add("BACKUP", "Critical workloads with backup", bad, len(crit), [f"CRITICAL {r['id']} has no backup" for r in bad])
    bad = [a for a in acc if not a["budget_alert"]]
    add("BUDGET", "Accounts with budget alerts", bad, len(acc), [f"{a['id']} has no budget alert" for a in bad])
    bad = [a for a in acc if not a["in_org"] or not a["owner"]]
    add("ORG_ACCOUNTS", "Accounts in org with named owner", bad, len(acc), [f"{a['id']}: " + ("outside org " if not a["in_org"] else "") + ("no owner" if not a["owner"] else "") for a in bad])
    from collections import Counter
    top, n = Counter(r["region"] for r in R).most_common(1)[0]; share = 100.0 * n / len(R)
    out["CONC"] = {"id": "CONC", "name": "Region concentration within appetite (<=40%)", "pct": round(min(100.0, 100.0 * (100 - share) / 60), 1), "total": len(R),
                   "n_findings": 1 if share > 40 else 0, "findings": [f"{share:.0f}% of estate sits in {top}"] if share > 40 else [], "waste_usd_month": 0}
    return out
