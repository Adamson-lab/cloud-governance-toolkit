import argparse, csv, json, os
from . import scoring, report, server
p = argparse.ArgumentParser(prog="toolkit"); sp = p.add_subparsers(dest="cmd", required=True)
a = sp.add_parser("assess"); a.add_argument("--answers", required=True); a.add_argument("--inventory", required=True); a.add_argument("--out", default="out"); a.add_argument("--title", default="Cloud Governance Assessment")
s = sp.add_parser("serve"); s.add_argument("--port", type=int, default=8081)
n = p.parse_args()
if n.cmd == "serve":
    print(f"Live toolkit -> http://localhost:{n.port}", flush=True); server.serve(n.port).serve_forever()
else:
    res = scoring.assess(json.load(open(n.answers, encoding="utf-8")), json.load(open(n.inventory, encoding="utf-8"))); os.makedirs(n.out, exist_ok=True)
    open(os.path.join(n.out, "report.html"), "w", encoding="utf-8").write(report.render(res, n.title))
    open(os.path.join(n.out, "radar.svg"), "w", encoding="utf-8").write(report.radar_svg(res["domains"]))
    open(os.path.join(n.out, "say_do_gap.svg"), "w", encoding="utf-8").write(report.gap_svg(res["domains"]))
    json.dump({k: res[k] for k in ("summary", "domains", "roadmap")}, open(os.path.join(n.out, "assessment.json"), "w"), indent=1)
    with open(os.path.join(n.out, "roadmap.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(res["roadmap"][0])); w.writeheader(); w.writerows(res["roadmap"])
    S = res["summary"]; print(f"Overall L{S['level']} {scoring.LEVELS[S['level']]} ({S['score']}/100) | say-do gap {S['avg_gap']:+.0f} | idle waste ${S['idle_waste_annual']:,.0f}/yr | outputs in {n.out}/")
