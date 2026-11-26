# Methodology and executive brief

## The five questions this toolkit makes a board able to ask
1. **Who is accountable, by name, for cloud risk and cloud spend?** (ORG-1, ORG-3)
2. **What do we say we do, and what does telemetry show?** The say-do gap is the headline number.
3. **Which single failed control is capping us?** Weakest-link rule: one failed critical control caps its whole domain.
4. **What does the waste and unallocated spend cost per year?** Quantified from the inventory, not estimated.
5. **What do we fix first?** Roadmap ranked by impact divided by effort, grouped into 0-30, 30-90 and 90-180 day horizons.

## Scoring
```
self score      yes=100  partial=50  no=0
measured score  strict(pass%) = max(0, (pass% - 50) * 2)     # 50% compliance or worse scores zero
control score   self only                    if no telemetry is available
                0.4 * self + 0.6 * measured if telemetry exists   # evidence outweighs opinion
domain score    weighted mean of its controls (weights 1-3)
domain level    L1 <20  L2 <40  L3 <60  L4 <80  L5 >=80
caps            critical control (weight 3) measured < 30 -> domain max L2 ; < 60 -> domain max L3
overall level   min( level(mean of domains), weakest domain level + 1 )
say-do gap      weighted self score minus weighted measured score, over controls that have telemetry
```
Why strict: a control that fails for one identity in three is not "two-thirds mature". Regulators and incident post-mortems treat it as failed.

## Using your own estate
Export your cloud inventory to the JSON shape in `examples/sample_inventory.json` (resources, iam, accounts, policy.allowed_regions). Map it from AWS Config, Azure Resource Graph or GCP Asset Inventory with a short script. Edit `toolkit/data/questions.json` to add, remove or reweight controls.

## Limits
- Self-reported answers are only as honest as the people giving them. Have the auditor, not the control owner, complete the non-telemetry questions.
- Scanner checks are point-in-time. Run them on a schedule and trend the result.
- Framework references are indicative mappings, not a certification.
