"""Generates the control library, a realistic messy sample estate, and two sample answer sets (deterministic)."""
import json, os, random
R = random.Random(7); ROOT = os.path.join(os.path.dirname(__file__), ".."); D = os.path.join(ROOT, "toolkit", "data"); E = os.path.join(ROOT, "examples")
# id, domain, question, scanner check, weight(1-3), effort(1-5), framework refs, remediation
Q = [
("ORG-1","Accountability","A named executive owns cloud risk AND spend, with authority to stop deployments.",None,3,2,"NIST CSF 2.0 GV.RR-01; ISO 27001 5.3","Appoint accountable executive; publish RACI; add to board charter"),
("ORG-2","Accountability","A cloud governance board meets monthly, with minuted decisions and tracked actions.",None,2,1,"NIST CSF 2.0 GV.OV; COBIT APO01","Stand up board; 60-min monthly cadence; action log"),
("ORG-3","Accountability","Every cloud account sits in the central organization with a named owner.","ORG_ACCOUNTS",3,3,"CIS 1.1; FedRAMP CM-8","Sweep shadow accounts; enforce org SCPs; require owner at creation"),
("IAM-1","Identity","MFA is enforced for every human identity, including root/break-glass.","MFA",3,2,"NIST 800-53 IA-2(1); CIS 1.5; PCI 8.4","Enforce phishing-resistant MFA via conditional access; vault root"),
("IAM-2","Identity","No wildcard admin policies; privileges are reviewed at least quarterly.","WILDCARD",3,4,"NIST AC-6; ISO 27001 A.8.2","Replace *:* with scoped roles; quarterly access recertification"),
("IAM-3","Identity","Dormant identities are disabled within 90 days.","STALE",2,2,"NIST AC-2(3); SOX ITGC","Automate joiner-mover-leaver and 90-day dormancy disable"),
("FIN-1","FinOps","Every resource carries owner and cost-center tags, enforced at deploy time.","TAGS",3,3,"FinOps Framework: Allocation","Tag-or-deny policy; backfill from CMDB; showback reports"),
("FIN-2","FinOps","Every account has a budget with alerts routed to the cost owner.","BUDGET",2,1,"FinOps: Planning & Forecasting","Budget-per-account via IaC baseline; alert to owner not mailbox"),
("FIN-3","FinOps","Idle and orphaned resources are reviewed and reclaimed monthly.","IDLE",2,2,"FinOps: Usage Optimization","Auto-schedule dev/test; rightsizing review; reclaim owner-less assets"),
("SEC-1","Security","No storage is publicly reachable without a time-boxed, approved exception.","PUBLIC",3,2,"CIS 3.3; NIST AC-3; FFIEC","Block public access at org level; exception register with expiry"),
("SEC-2","Security","All data stores are encrypted at rest with managed keys and rotation.","ENCRYPT",3,3,"NIST SC-28; PCI 3.5; ISO A.8.24","Enable default encryption; deny unencrypted creates; rotate keys"),
("SEC-3","Security","Continuous control monitoring reports to executives against a named framework.",None,2,3,"NIST CSF 2.0 GV.OV-03; FedRAMP ConMon","Deploy CSPM; map to framework; monthly exec scorecard"),
("DAT-1","Data & Sovereignty","Data residency is technically enforced by an approved-region allow-list.","REGION",3,3,"GDPR Ch.V; DORA Art.28; Nigeria NDPA; FedRAMP","Org-level region-deny policy; migrate or exception-register offenders"),
("DAT-2","Data & Sovereignty","All data stores carry a classification label that drives controls.",None,2,4,"ISO 27001 A.5.12; NIST RA-2","Classification taxonomy; auto-label; link to encryption/residency"),
("DAT-3","Data & Sovereignty","Retention schedules and legal holds are defined and enforced in cloud storage.",None,2,3,"NARA/records mgmt; SOX 802","Retention policies per class; legal-hold workflow with legal team"),
("RES-1","Resilience","Every critical workload has automated, restore-tested backups.","BACKUP",3,3,"NIST CP-9; DORA Art.12; FFIEC BCM","Backup-by-default for tier-1; quarterly restore tests"),
("RES-2","Resilience","Disaster recovery is tested at least annually with evidenced RTO/RPO.",None,3,4,"NIST CP-4; DORA Art.11/24; ISO 22301","Annual DR exercise; evidence pack for regulators"),
("RES-3","Resilience","A tested exit and portability plan exists for every critical cloud service.",None,2,5,"DORA Art.28(8); EBA Outsourcing; OCC 2023-17","Exit plans per critical service; stressed-exit tabletop"),
("AUT-1","Automation","Policy-as-code guardrails block non-compliant deployments before they land.",None,3,4,"NIST CM-2/CM-6; CIS Benchmarks","OPA/SCP guardrails in CI and at org level"),
("AUT-2","Automation","Infrastructure changes occur only through reviewed IaC pipelines.",None,2,4,"NIST CM-3; SOX change mgmt","Remove console write access; pipeline-only deploys"),
("AUT-3","Automation","Policy exceptions are time-boxed, approved, and expire automatically.",None,2,2,"NIST CA-5 (POA&M)","Exception register with owner, expiry, auto-revoke"),
("TPR-1","Third-Party Risk","Provider and region concentration risk is measured and within board appetite.","CONC",3,4,"DORA Art.29; BoE/PRA SS2/21; FSB","Set concentration appetite; multi-region for tier-1"),
("TPR-2","Third-Party Risk","Contracts give audit rights, incident notice SLAs and sub-processor visibility.",None,2,3,"DORA Art.30; GDPR Art.28","Contract addendum program for top-20 providers"),
("TPR-3","Third-Party Risk","SaaS and shadow-IT inventory is complete and risk-tiered.",None,2,3,"ISO 27001 A.5.19-5.22; NIST SR-6","CASB/SSPM discovery; tier and onboard"),
]
os.makedirs(D, exist_ok=True); os.makedirs(E, exist_ok=True)
json.dump([dict(zip(("id","domain","q","check","w","e","refs","fix"), q)) for q in Q], open(os.path.join(D, "questions.json"), "w"), indent=1)
reg = lambda: R.choices(["us-east-1","eu-west-1","ap-southeast-1","af-south-1"], [58,30,7,5])[0]
res = []
for i in range(220):
    t = R.choices(["vm","k8s","bucket","db","disk"], [35,10,20,15,20])[0]
    lo, hi = dict(vm=(80,900), k8s=(400,3000), bucket=(5,300), db=(150,2500), disk=(10,120))[t]
    tags = {}
    if R.random() < .62: tags = {"owner": f"team-{R.randint(1,12)}", "cost_center": f"CC{R.randint(100,140)}"}
    elif R.random() < .5: tags = {"owner": f"team-{R.randint(1,12)}"}
    crit = t in ("vm","db","k8s") and R.random() < .2
    res.append({"id": f"{t}-{i:03d}", "type": t, "region": reg(), "tags": tags, "cost": round(R.uniform(lo, hi), 2),
        "public": t == "bucket" and R.random() < .14, "encrypted": R.random() < .84, "critical": crit,
        "cpu_avg": round(R.uniform(1, 70) if R.random() > .22 else R.uniform(0.2, 4.5), 1) if t in ("vm","k8s") else None,
        "backup": R.random() < (.55 if crit else .4)})
inv = {"policy": {"allowed_regions": ["us-east-1","eu-west-1"]}, "resources": res,
  "iam": {"root_mfa": False, "users": [{"name": f"user{i}", "mfa": R.random() < .78, "last_used_days": R.choice([3,10,30,60,120,200,400]) if R.random() < .75 else R.randint(95,500)} for i in range(60)],
          "policies": [{"name": f"policy-{i}", "wildcard": R.random() < .2} for i in range(40)]},
  "accounts": [{"id": f"acct-{i:02d}", "in_org": R.random() < .84, "owner": (f"team-{i}" if R.random() < .8 else ""), "budget_alert": R.random() < .52} for i in range(25)]}
json.dump(inv, open(os.path.join(E, "sample_inventory.json"), "w"), indent=1)
ids = [q[0] for q in Q]
over = {i: "yes" for i in ids}; over["RES-2"] = over["AUT-3"] = "partial"
json.dump(over, open(os.path.join(E, "answers_overconfident.json"), "w"), indent=1)
honest = {"ORG-1":"yes","ORG-2":"partial","SEC-3":"partial","DAT-2":"partial","DAT-3":"yes","RES-2":"no","RES-3":"no","AUT-1":"no","AUT-2":"partial","AUT-3":"no","TPR-2":"partial","TPR-3":"no"}
json.dump(honest, open(os.path.join(E, "answers_honest_partial.json"), "w"), indent=1)
print("generated", len(Q), "controls,", len(res), "resources")
