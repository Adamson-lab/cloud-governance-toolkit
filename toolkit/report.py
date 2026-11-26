"""Renders the board report (self-contained HTML) plus the radar and say-do-gap SVG diagrams."""
import html as _h, math
from .scoring import LEVELS
esc = lambda s: _h.escape(str(s))
GRID, CUR, TGT, SELF, MEAS = "#8b949e", "#c0392b", "#2e8b57", "#e6a23c", "#3b82c4"

def radar_svg(domains, target=4.0):
    cx, cy, R, n = 250, 245, 150, len(domains)
    def pt(i, v): a = math.radians(-90 + i * 360 / n); return cx + R * v / 5 * math.cos(a), cy + R * v / 5 * math.sin(a)
    poly = lambda vals: " ".join("%.1f,%.1f" % pt(i, v) for i, v in enumerate(vals))
    o = ["<svg xmlns='http://www.w3.org/2000/svg' width='500' height='510' viewBox='0 0 500 510' font-family='system-ui,Segoe UI,Arial' font-size='12'>",
         "<text x='250' y='22' text-anchor='middle' font-size='15' font-weight='700' fill='#8b949e'>Cloud Governance Maturity</text>"]
    for lv in range(1, 6): o.append(f"<polygon points='{poly([lv]*n)}' fill='none' stroke='{GRID}' stroke-opacity='.4'/><text x='{cx+4}' y='{cy-R*lv/5+11}' fill='{GRID}' font-size='10'>L{lv}</text>")
    for i, d in enumerate(domains):
        x, y = pt(i, 5); lx, ly = pt(i, 5.75)
        o.append(f"<line x1='{cx}' y1='{cy}' x2='{x:.1f}' y2='{y:.1f}' stroke='{GRID}' stroke-opacity='.4'/>")
        o.append(f"<text x='{lx:.0f}' y='{ly:.0f}' text-anchor='{'middle' if abs(lx-cx)<20 else 'start' if lx>cx else 'end'}' fill='{GRID}' font-weight='600'>{esc(d['name'])}</text>")
    o.append(f"<polygon points='{poly([target]*n)}' fill='none' stroke='{TGT}' stroke-width='2' stroke-dasharray='6 4'/>")
    vals = [max(0.15, d["score"] / 20) for d in domains]
    o.append(f"<polygon points='{poly(vals)}' fill='{CUR}' fill-opacity='.28' stroke='{CUR}' stroke-width='2.5'/>")
    for i, (d, v) in enumerate(zip(domains, vals)):
        x, y = pt(i, v); o.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='4.5' fill='{CUR}'><title>{esc(d['name'])}: {d['score']}/100 (L{d['level']})</title></circle>")
    o.append(f"<rect x='150' y='484' width='14' height='10' fill='{CUR}' fill-opacity='.5'/><text x='170' y='493' fill='{GRID}'>Current (evidence-weighted)</text>"
             f"<line x1='330' y1='489' x2='352' y2='489' stroke='{TGT}' stroke-width='2' stroke-dasharray='6 4'/><text x='358' y='493' fill='{GRID}'>Target L{target:.0f}</text></svg>")
    return "".join(o)

def gap_svg(domains):
    h = 40 + 46 * len(domains)
    o = [f"<svg xmlns='http://www.w3.org/2000/svg' width='560' height='{h}' viewBox='0 0 560 {h}' font-family='system-ui,Segoe UI,Arial' font-size='12'>",
         f"<text x='10' y='18' font-weight='700' fill='{GRID}'>Say-do gap: what we report vs what telemetry shows</text>",
         f"<rect x='330' y='8' width='10' height='10' fill='{SELF}'/><text x='344' y='17' fill='{GRID}'>self</text><rect x='385' y='8' width='10' height='10' fill='{MEAS}'/><text x='399' y='17' fill='{GRID}'>measured</text>"]
    for i, d in enumerate(domains):
        y = 34 + 46 * i; o.append(f"<text x='10' y='{y+20}' fill='{GRID}' font-weight='600'>{esc(d['name'])}</text>")
        if d["measured"] is None: o.append(f"<text x='150' y='{y+20}' fill='{GRID}' font-style='italic'>no telemetry available: self-reported only</text>"); continue
        for k, (v, c) in enumerate(((d["self_linked"], SELF), (d["measured"], MEAS))):
            o.append(f"<rect x='150' y='{y+k*16}' width='{v*3.2:.0f}' height='13' fill='{c}' rx='2'/><text x='{156+v*3.2:.0f}' y='{y+11+k*16}' fill='{GRID}'>{v:.0f}%</text>")
        if d["gap"] > 15: o.append(f"<text x='490' y='{y+20}' fill='{CUR}' font-weight='700'>+{d['gap']:.0f} gap</text>")
    return "".join(o) + "</svg>"

CSS = """:root{--bg:#fff;--fg:#1f2328;--mut:#656d76;--card:#f6f8fa;--bd:#d0d7de}@media(prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--mut:#8b949e;--card:#161b22;--bd:#30363d}}
body{background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,Segoe UI,Arial;max-width:1100px;margin:0 auto;padding:1.2rem}h1{margin:.2rem 0}h2{border-bottom:1px solid var(--bd);padding-bottom:.3rem;margin-top:2rem}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.k div{background:var(--card);border:1px solid var(--bd);border-radius:8px;padding:10px}.k b{font-size:22px;display:block}.k span{color:var(--mut);font-size:12px}
table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid var(--bd);padding:5px 8px;text-align:left;font-size:13px;vertical-align:top}.hm td{color:#fff;text-align:center;font-weight:600;border:2px solid var(--bg)}
.row{display:flex;gap:1.5rem;flex-wrap:wrap;align-items:flex-start}.bar{display:inline-block;height:8px;background:#3b82c4;border-radius:3px}.bad{color:#c0392b;font-weight:700}.mut{color:var(--mut)}code{font-size:12px}"""

def render(res, title="Cloud Governance Assessment"):
    S, D, rows = res["summary"], res["domains"], res["rows"]
    kp = [(f"L{S['level']} {LEVELS[S['level']]}", f"Overall maturity ({S['score']}/100)"), (f"{S['avg_gap']:+.0f} pts", "Say-do gap: self-reported minus measured"),
          (f"${S['idle_waste_annual']:,.0f}", "Idle compute waste per year"), (f"{S['unallocated_pct']:.0f}%", f"Spend with no owner/cost-center (of ${S['monthly_cost']:,}/mo)"),
          (S["public_buckets"], "Publicly exposed buckets"), (S["no_mfa"], "Identities without MFA")]
    o = [f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>{esc(title)}</title><style>{CSS}</style>",
         f"<h1>{esc(title)}</h1><div class=mut>Evidence-weighted: measured telemetry counts 60%, self-reported answers 40%. Measured scores are strict: 50% compliance or worse scores zero.</div><h2>Board summary</h2><div class=k>"]
    o += [f"<div><b>{esc(a)}</b><span>{esc(b)}</span></div>" for a, b in kp] + ["</div><ul>"]
    for g in sorted([d for d in D if d["gap"] is not None], key=lambda d: -d["gap"])[:3]:
        o.append(f"<li><b>{esc(g['name'])}</b>: leadership reports <b>{g['self_linked']:.0f}%</b>, telemetry shows <b>{g['measured']:.0f}%</b> ({g['gap']:+.0f} pts).</li>")
    o.append(f"<li>Weakest domains: <b>{esc(', '.join(S['weakest']))}</b>. {S['critical_no_backup']} critical workloads lack backup; {S['outside_region']} resources sit outside approved regions.</li></ul>")
    o.append(f"<h2>Maturity profile</h2><div class=row>{radar_svg(D)}{gap_svg(D)}</div><table><tr><th>Domain<th>Score<th>Level<th>Self (linked)<th>Measured<th>Note")
    for d in D: o.append(f"<tr><td>{esc(d['name'])}<td>{d['score']}<td>L{d['level']} {LEVELS[d['level']]}<td>{'' if d['self_linked'] is None else str(d['self_linked'])+'%'}<td>{'' if d['measured'] is None else str(d['measured'])+'%'}<td>{('capped by <code>'+d['capped_by']+'</code> (weakest link)') if d['capped_by'] else ''}")
    o.append("</table><h2>Control heatmap</h2><table class=hm>")
    for d in D:
        o.append(f"<tr><th style='text-align:left;color:var(--fg)'>{esc(d['name'])}")
        for r in [r for r in rows if r["domain"] == d["name"]]: o.append(f"<td style='background:hsl({r['score']*1.2:.0f},55%,38%)' title='{esc(r['q'])} | self {r['self']:.0f}% measured {r['measured'] if r['measured'] is not None else 'n/a'}'>{r['id']}<br>{r['score']:.0f}")
    o.append("</table><h2>Evidence: what the scan found</h2><table><tr><th>Measure<th>Pass<th>Examples")
    for c in sorted(res["checks"].values(), key=lambda c: c["pct"]):
        o.append(f"<tr><td>{esc(c['name'])}<td><span class=bar style='width:{c['pct']*0.8:.0f}px'></span> {c['pct']:.0f}%<td class=mut>{esc('; '.join(c['findings'][:3])) or 'none'}")
    o.append("</table><h2>Prioritized roadmap (impact / effort)</h2>")
    for hz in ("0-30 days", "30-90 days", "90-180 days"):
        items = [x for x in res["roadmap"] if x["horizon"] == hz][:6]
        o.append(f"<h3>{hz}</h3><table><tr><th>Control<th>Action<th>Impact<th>Effort<th>Frameworks")
        o += [f"<tr><td><code>{x['id']}</code> {esc(x['domain'])}<td>{esc(x['action'])}<td>{x['impact']}<td>{x['effort']}/5<td class=mut>{esc(x['refs'])}" for x in items] or ["<tr><td colspan=5 class=mut>nothing in this horizon"]
        o.append("</table>")
    return "".join(o)
