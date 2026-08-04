---
name: handling-china-ma-transactions
description: Use when advising on China-focused investment or M&A transactions, including legal due diligence, transaction structuring, listed-company control acquisitions, private share or asset purchases, SPA/APA terms, regulatory approvals, signing or closing, negotiation, and buyer- or seller-side issue analysis.
---

# Handling China M&A Transactions

## Product

Treat this as a **中国投资并购决策与执行 Skill**. Use this **三维决策内核**:

1. **控制权**：define what power or rights end-state the transaction must achieve and when;
2. **收购方式**：compare the tools, combinations and sequence used to reach that state;
3. **合并财务报表**：test whether the resulting facts support the intended accounting assessment and evidence package.

Diligence, approvals, documents, negotiation and closing are execution layers serving the three axes. They do not replace the kernel.

## Core rules

- Default to the buyer perspective when the user does not state a side. Declare `Perspective: Buyer`; when asked for the seller, declare `Perspective: Seller` and switch substantively.
- Use the three-axis kernel before working the lifecycle: structure → contact/NDA → diligence → documents/negotiation → signing → effectiveness/approvals → closing → post-closing/integration → claims.
- Keep legal authority, regulatory/case observation, historical/draft material and market playbook separate.
- Treat the supplied listed-company article and deal tables as issue seeds, never as controlling authority.
- Convert every material fact into a transaction response: price, CP, deliverable, warranty/disclosure, indemnity/limitation, covenant, termination, security or post-close action.
- Never promise an approval, consolidation, registration, tax treatment or foreign-law result.

## Start every matter

Read [intake-routing-and-gates.md](references/intake-routing-and-gates.md) and [legal-authority-protocol.md](references/legal-authority-protocol.md). Establish the matter profile, as-of date, route, stage, confidentiality level, missing facts, requested deliverable and completion state.

For an unannounced listed-company transaction, treat MNPI as a hard gate. Do not put names, prices, unannounced structures or document text into external searches. Use abstract legal queries and the least necessary information.

## Run the three-axis kernel

Read [three-axis-transaction-engine.md](references/three-axis-transaction-engine.md) for every transaction matter. Assign each axis `required`, `not-sought`, `not-applicable`, `pending-professional-confirmation` or `blocked`; never omit an axis silently.

- `L-CONTROL`: always complete all three axes.
- `P-EQUITY` and `P-ASSET`: adapt the meaning to the route and state expressly when control or consolidation is not pursued or requires professional confirmation.
- Structure requests: compare at least three paths when facts permit; otherwise state each eliminated path and its reason.
- Non-structure requests: identify the affected axes without fabricating a full structure memorandum.

## Route

| Route | Use for | Required reference |
|---|---|---|
| `L-CONTROL` | PRC listed-company control or potential-control acquisitions | [listed-control.md](references/listed-control.md) |
| `P-EQUITY` | Private-company share/equity acquisitions, control investments, staged deals and statutory-merger comparison | [private-equity-ma.md](references/private-equity-ma.md) |
| `P-ASSET` | Asset/business purchases and carve-outs | [private-asset-ma.md](references/private-asset-ma.md) |

Combine routes only for a real hybrid. For pure minority financing with no control, business or asset acquisition, record the three-axis boundary, prepare [pe-vc-handoff-template.md](assets/pe-vc-handoff-template.md), then invoke `$pe-vc-transaction-docs-review`. If its document review finds rights that may create control, joint control or decisive influence, return to this Skill for `P-EQUITY` and regulatory analysis.

## Load only what the task needs

- Diligence or issue lists: [due-diligence-playbook.md](references/due-diligence-playbook.md).
- SPA/APA review, price, clauses or negotiation: [positions-and-documents.md](references/positions-and-documents.md).
- Merger control, SOE, foreign investment, ODI/FX, data, sector, labor, IP or tax interfaces: [regulatory-overlays.md](references/regulatory-overlays.md).
- Consolidation or purchase-date questions: [accounting-control-and-consolidation.md](references/accounting-control-and-consolidation.md).
- The supplied article, Taisheng Wind Power conditions or historical approval table: [article-and-deal-seeds.md](references/article-and-deal-seeds.md).
- The mandatory control → acquisition method → consolidation workflow: [three-axis-transaction-engine.md](references/three-axis-transaction-engine.md).
- Deliverable structure and completion state: [output-contract.md](references/output-contract.md).

The structured authority registry is [legal-authorities.json](references/legal-authorities.json). Do not load it wholesale. Query it:

```bash
python3 scripts/legal_authority_lookup.py --route L-CONTROL --effective-only
python3 scripts/legal_authority_lookup.py --topic merger-control --as-of YYYY-MM-DD --json
python3 scripts/legal_authority_lookup.py --topic listed-issuance --freshness-days 30
```

If signing, filing, announcing, closing or giving a high-stakes conclusion, open and verify the current official instrument in the same task. The registry is a versioned navigation aid, not a substitute for verification.

Any approval or regulatory checklist must assign each item to `pre-signing`, `effectiveness`, `pre-closing`, `post-closing` or `continuing`; do not return one undifferentiated list.

## Work the closed loop

For every material issue, record:

1. Confirmed fact and exact source/version;
2. Missing fact and evidence needed;
3. Current official basis, pinpoint and verification date;
4. Risk event and transaction impact;
5. Primary structure/price/term response;
6. Buyer and seller positions;
7. Fallback, reciprocal give/get and walk-away/escalation point;
8. Owner, deadline, closing evidence and status.

Do not use unsupported percentages as “China market practice.” If a statistic is relevant, state jurisdiction, sample, period, transaction type and that it is not law.

Even a quick risk list must keep a per-issue owner and status, plus the evidence needed to close it. A seller-side liability plan must expressly address cap, de minimis, basket, survival, knowledge qualifiers, disclosure, warranty/risk classes, concession sequence and fallbacks; do not hide these inside generic “reasonable limitation” language.

## Control and timing discipline

- Separate securities-law control, governance control, merger-control control, accounting control and foreign-investment/security-review control.
- Separate shareholding, owned interests, exercisable voting power, meeting votes, fully diluted ownership and accounting power.
- For the 30% offer line, identify on-market, agreement, indirect, issuance or tender-offer route before choosing the rule.
- Separate signing, contractual effectiveness, regulatory clearance, share/asset transfer, governance change, control acquisition, accounting purchase date and post-close registration.
- Do not use a warranty or indemnity to replace a legal prohibition, approval or standstill.

## Outputs

Use these assets when useful:

- [matter-intake-template.md](assets/matter-intake-template.md)
- [due-diligence-issue-list-template.md](assets/due-diligence-issue-list-template.md)
- [approval-matrix-template.md](assets/approval-matrix-template.md)
- [negotiation-plan-template.md](assets/negotiation-plan-template.md)
- [three-axis-structure-template.md](assets/three-axis-structure-template.md)
- [pe-vc-handoff-template.md](assets/pe-vc-handoff-template.md)

The first page must state matter, route, perspective, as-of date, materials/versions, assumptions, jurisdiction and one of: `passed`, `passed_with_limitations`, `blocked`.

## Boundaries

- PRC law is the v1 hard-authority scope. For a foreign target, the response is incomplete unless it provides the applicable China-side ODI, FX, SOE, merger-control, data/technology-export and export-control checklist, while assigning foreign-law confirmation to qualified local counsel. In v1, do not search for, quote, calculate or state foreign filing thresholds—even with a disclaimer—because no foreign authority/version protocol has been built.
- Tax, valuation, accounting, environmental, technical and sector issues are identified and routed; do not replace the responsible professional.
- Do not claim full diligence when documents are missing, unreadable, outside the agreed sample or not updated to the delivery date.

## Validate before delivery

Run:

```bash
python3 scripts/validate_legal_authorities.py
python3 scripts/validate_skill_consistency.py
```

Disclose unverified law, missing files, foreign-law dependencies and any limitation that prevents a reliable recommendation.
