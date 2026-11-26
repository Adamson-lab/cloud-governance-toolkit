import json, os, sys, threading, unittest, urllib.request
ROOT = os.path.join(os.path.dirname(__file__), ".."); sys.path.insert(0, ROOT)
from toolkit import scanner, scoring, report, server
L = lambda n: json.load(open(os.path.join(ROOT, "examples", n), encoding="utf-8"))
INV, OVER, HON = L("sample_inventory.json"), L("answers_overconfident.json"), L("answers_honest_partial.json")

class T(unittest.TestCase):
    def test_scanner_finds_planted_issues(self):
        c = scanner.run(INV); self.assertGreater(c["PUBLIC"]["n_findings"], 0); self.assertGreater(c["IDLE"]["waste_usd_month"], 0)
        self.assertIn("ROOT account has no MFA", c["MFA"]["findings"]); self.assertTrue(all(0 <= v["pct"] <= 100 for v in c.values()))
    def test_overconfidence_creates_positive_say_do_gap(self):
        r = scoring.assess(OVER, INV); self.assertGreater(r["summary"]["avg_gap"], 20)
        self.assertLess(r["summary"]["level"], 4)   # telemetry must drag a self-declared "all yes" down
    def test_evidence_outweighs_opinion(self):
        self.assertLess(scoring.assess(OVER, INV)["summary"]["score"], 85)
    def test_weakest_link_cap(self):
        d = {x["name"]: x for x in scoring.assess(OVER, INV)["domains"]}; self.assertIsNotNone(d["Identity"]["capped_by"]); self.assertLessEqual(d["Identity"]["level"], 3)
    def test_honest_answers_reduce_gap(self):
        c = scanner.run(INV); h = dict(HON)
        for q in scoring.QUESTIONS:
            if q["check"]: h[q["id"]] = "yes" if c[q["check"]]["pct"] >= 90 else "partial" if c[q["check"]]["pct"] >= 70 else "no"
        self.assertLess(abs(scoring.assess(h, INV)["summary"]["avg_gap"]), scoring.assess(OVER, INV)["summary"]["avg_gap"] / 2)
    def test_report_has_diagrams_and_roadmap(self):
        h = report.render(scoring.assess(OVER, INV)); self.assertIn("<svg", h); self.assertIn("Prioritized roadmap", h); self.assertIn("Say-do gap", h)
    def test_api(self):
        s = server.serve(0); threading.Thread(target=s.serve_forever, daemon=True).start(); p = s.server_address[1]
        r = urllib.request.Request(f"http://127.0.0.1:{p}/api/assess", data=json.dumps({"answers": OVER}).encode(), method="POST")
        j = json.loads(urllib.request.urlopen(r).read()); self.assertIn("summary", j); self.assertIn("<svg", j["html"]); s.shutdown()
if __name__ == "__main__": unittest.main()
