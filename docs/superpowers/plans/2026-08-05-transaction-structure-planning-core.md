# Transaction Structure Planning Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refocus `handling-china-ma-transactions` into a fixed-interface transaction-structure planning Skill that produces one structured analysis, two audience views, and four downstream task packages without claiming to execute the downstream work.

**Architecture:** Keep the existing technical skill identifier for compatibility. Replace the broad lifecycle contract with a six-group input contract, a fixed three-axis planning engine, an eight-part output contract, and a single downstream-package schema. Route and legal references become planning constraints; full diligence, document review, negotiation, filing, accounting conclusions, integration, and claims leave the core workflow.

**Tech Stack:** Markdown Skill resources, YAML UI metadata, Python `unittest` consistency validator, JSON legal-authority registry.

---

## File map

- Modify `skills/handling-china-ma-transactions/SKILL.md`: concise planning workflow and resource routing.
- Modify `skills/handling-china-ma-transactions/references/intake-routing-and-gates.md`: six input groups, requirement levels, fact states, start/recommendation gates.
- Modify `skills/handling-china-ma-transactions/references/three-axis-transaction-engine.md`: fixed eight-step analysis and three-path comparison.
- Modify `skills/handling-china-ma-transactions/references/output-contract.md`: eight outputs, dual views, consistency rules, boundaries.
- Modify `skills/handling-china-ma-transactions/references/listed-control.md`: listed-control structure-planning branch only.
- Modify `skills/handling-china-ma-transactions/references/private-equity-ma.md`: private-equity structure-planning branch only.
- Modify `skills/handling-china-ma-transactions/references/private-asset-ma.md`: asset/business structure-planning branch only.
- Modify `skills/handling-china-ma-transactions/references/regulatory-overlays.md`: approval constraints and approval-task-package interface only.
- Modify `skills/handling-china-ma-transactions/references/accounting-control-and-consolidation.md`: evidence package and accountant handoff only.
- Keep `skills/handling-china-ma-transactions/references/legal-authority-protocol.md`, `legal-authorities.json`, and `article-and-deal-seeds.md`: authority governance and issue seeds.
- Modify `skills/handling-china-ma-transactions/assets/matter-intake-template.md`: fixed input interface.
- Modify `skills/handling-china-ma-transactions/assets/three-axis-structure-template.md`: fixed eight-part output with management and lawyer views.
- Create `skills/handling-china-ma-transactions/assets/downstream-task-packages-template.md`: common schema plus four packages.
- Delete `skills/handling-china-ma-transactions/assets/due-diligence-issue-list-template.md`, `approval-matrix-template.md`, `negotiation-plan-template.md`, and `pe-vc-handoff-template.md`: no longer core outputs.
- Delete `skills/handling-china-ma-transactions/references/due-diligence-playbook.md` and `positions-and-documents.md` after migrating structure-specific rules.
- Modify `skills/handling-china-ma-transactions/agents/openai.yaml`: new display name and planning-only prompt.
- Modify `README.md`: quick-start product page for the narrowed capability.
- Modify `skills/handling-china-ma-transactions/scripts/tests/test_validate_skill_consistency.py`: executable product-contract tests.
- Modify `skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py`: validate the new contract and reject overclaiming.

### Task 1: Write the failing fixed-interface tests

**Files:**
- Modify: `skills/handling-china-ma-transactions/scripts/tests/test_validate_skill_consistency.py`

- [ ] **Step 1: Replace obsolete PE/VC and execution-asset tests with input-contract tests**

Add assertions equivalent to:

```python
def test_intake_defines_six_groups_and_two_state_dimensions(self):
    text = (ROOT / "assets" / "matter-intake-template.md").read_text(encoding="utf-8")
    for token in (
        "事项信息", "商业目标", "交易事实", "可选路径", "硬约束", "材料与缺口",
        "start-required", "assumption-allowed", "recommendation-blocker",
        "confirmed", "assumed", "missing", "conflicting",
        "external-confirmation-pending",
    ):
        self.assertIn(token, text)
```

- [ ] **Step 2: Add output, dual-view, package, and boundary tests**

```python
def test_output_contract_has_eight_sections_and_two_views(self):
    text = (ROOT / "references" / "output-contract.md").read_text(encoding="utf-8")
    for token in (
        "项目状态及分析边界", "一页式方案结论", "三维目标及当前状态",
        "基准、备选、兜底", "推荐方案、推荐理由及成立条件",
        "关键反证、缺失事实和待决策事项",
        "签署—审批—交割—控制取得—并表判断时间线", "后续任务包",
        "管理层决策版", "律师执行版", "同一底层分析",
    ):
        self.assertIn(token, text)

def test_downstream_template_has_four_packages_and_common_schema(self):
    text = (ROOT / "assets" / "downstream-task-packages-template.md").read_text(encoding="utf-8")
    for token in (
        "尽调任务包", "交易文件任务包", "审批任务包", "会计任务包",
        "Package ID", "来源方案/维度", "完成证据", "结果回传字段",
    ):
        self.assertIn(token, text)
```

Add negative-validator tests that remove one input group, remove one output section, remove one package, or insert `完成全面尽调` into `SKILL.md`, then assert the validator reports the exact missing/overclaim error.

- [ ] **Step 3: Run the consistency test and verify RED**

Run:

```bash
python3 -m unittest scripts.tests.test_validate_skill_consistency -v
```

Expected: FAIL because the old Skill lacks the new fixed input, output, package, and boundary contracts.

- [ ] **Step 4: Commit the RED tests**

```bash
git add skills/handling-china-ma-transactions/scripts/tests/test_validate_skill_consistency.py
git commit -m "test: define structure planning product contract"
```

### Task 2: Implement the deterministic consistency contract

**Files:**
- Modify: `skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py`
- Test: `skills/handling-china-ma-transactions/scripts/tests/test_validate_skill_consistency.py`

- [ ] **Step 1: Replace old execution constants with fixed-interface constants**

Define constants for the six input groups, requirement levels, fact states, eight output sections, two views, four packages, common package fields, and forbidden overclaim phrases. Remove PE/VC-specific and full-execution-asset invariants.

- [ ] **Step 2: Add contract checks**

Validate that:

```python
for token in FIXED_INPUT_TOKENS:
    if token not in intake_text:
        errors.append(f"fixed input contract lacks token: {token}")

for token in FIXED_OUTPUT_TOKENS:
    if token not in output_text:
        errors.append(f"fixed output contract lacks token: {token}")

for phrase in FORBIDDEN_CAPABILITY_CLAIMS:
    if phrase in skill:
        errors.append(f"SKILL.md overclaims downstream execution: {phrase}")
```

Also require `assets/downstream-task-packages-template.md`, the four package names, common fields, and direct links from `SKILL.md`.

- [ ] **Step 3: Run the targeted tests**

Run:

```bash
python3 -m unittest scripts.tests.test_validate_skill_consistency -v
```

Expected: still FAIL on missing content, while the new mutation tests fail for their intended exact reasons.

- [ ] **Step 4: Commit the validator**

```bash
git add skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py
git commit -m "test: enforce fixed planning interfaces"
```

### Task 3: Build the fixed input, analysis, output, and handoff resources

**Files:**
- Modify: `skills/handling-china-ma-transactions/references/intake-routing-and-gates.md`
- Modify: `skills/handling-china-ma-transactions/references/three-axis-transaction-engine.md`
- Modify: `skills/handling-china-ma-transactions/references/output-contract.md`
- Modify: `skills/handling-china-ma-transactions/assets/matter-intake-template.md`
- Modify: `skills/handling-china-ma-transactions/assets/three-axis-structure-template.md`
- Create: `skills/handling-china-ma-transactions/assets/downstream-task-packages-template.md`

- [ ] **Step 1: Implement the six-group intake contract**

Use requirement-level and fact-state columns separately. State explicitly that `start-required` prevents starting, `recommendation-blocker` permits comparison but prevents a definitive recommendation, and every non-confirmed fact needs impact, owner, and closing evidence.

- [ ] **Step 2: Implement the fixed planning sequence**

Require the eight analysis steps from the approved spec, preserve control → path comparison → consolidation evidence causality, and require baseline/alternative/fallback or documented exclusions.

- [ ] **Step 3: Implement the eight-part output and dual views**

Make the management and lawyer outputs projections of the same IDs, facts, statuses, recommendation, and timeline. The management view stays concise; the lawyer view includes sources, dependencies, and task packages.

- [ ] **Step 4: Implement the downstream package asset**

Create one common table schema and four sections. Each package must be traceable to a方案 ID and axis and must contain a result-return field so downstream findings can reopen the planning decision.

- [ ] **Step 5: Run targeted tests and verify GREEN for these contracts**

```bash
python3 -m unittest scripts.tests.test_validate_skill_consistency -v
```

Expected: new input/output/package tests pass; remaining failures identify stale route, metadata, or README content.

- [ ] **Step 6: Commit the core resources**

```bash
git add skills/handling-china-ma-transactions/references/intake-routing-and-gates.md skills/handling-china-ma-transactions/references/three-axis-transaction-engine.md skills/handling-china-ma-transactions/references/output-contract.md skills/handling-china-ma-transactions/assets/matter-intake-template.md skills/handling-china-ma-transactions/assets/three-axis-structure-template.md skills/handling-china-ma-transactions/assets/downstream-task-packages-template.md
git commit -m "feat: add fixed structure planning interfaces"
```

### Task 4: Narrow the Skill and route references

**Files:**
- Modify: `skills/handling-china-ma-transactions/SKILL.md`
- Modify: `skills/handling-china-ma-transactions/references/listed-control.md`
- Modify: `skills/handling-china-ma-transactions/references/private-equity-ma.md`
- Modify: `skills/handling-china-ma-transactions/references/private-asset-ma.md`
- Modify: `skills/handling-china-ma-transactions/references/regulatory-overlays.md`
- Modify: `skills/handling-china-ma-transactions/references/accounting-control-and-consolidation.md`
- Delete: `skills/handling-china-ma-transactions/references/due-diligence-playbook.md`
- Delete: `skills/handling-china-ma-transactions/references/positions-and-documents.md`
- Delete: `skills/handling-china-ma-transactions/assets/due-diligence-issue-list-template.md`
- Delete: `skills/handling-china-ma-transactions/assets/approval-matrix-template.md`
- Delete: `skills/handling-china-ma-transactions/assets/negotiation-plan-template.md`
- Delete: `skills/handling-china-ma-transactions/assets/pe-vc-handoff-template.md`

- [ ] **Step 1: Rewrite `SKILL.md` as a concise planning procedure**

Keep the technical name. Change the description to triggering conditions for transaction-structure planning. Require the fixed intake, three-axis sequence, eight outputs, two audience views, four handoffs, authority protocol, and explicit exclusions.

- [ ] **Step 2: Narrow route references**

Each route reference should answer only: how the route changes control targets, eligible paths, hard constraints, consolidation evidence, and handoff tasks. Remove broad end-to-end lifecycle and generic negotiation claims.

- [ ] **Step 3: Narrow approval and accounting references**

Regulatory content should identify constraints and populate an approval package, not claim filing execution. Accounting content should populate an evidence package, not conclude consolidation.

- [ ] **Step 4: Migrate any unique structure rule from obsolete files, then remove them**

Preserve only rules that affect path selection, conditions, sequencing, failure recovery, or evidence. Remove the obsolete files and all links to them.

- [ ] **Step 5: Run the consistency tests**

```bash
python3 -m unittest scripts.tests.test_validate_skill_consistency -v
```

Expected: route and core Skill contract tests pass; README/UI tests may remain red.

- [ ] **Step 6: Commit the scope refactor**

```bash
git add skills/handling-china-ma-transactions
git commit -m "refactor: narrow skill to structure planning"
```

### Task 5: Align the user-facing product page and UI metadata

**Files:**
- Modify: `README.md`
- Modify: `skills/handling-china-ma-transactions/agents/openai.yaml`
- Test: `skills/handling-china-ma-transactions/scripts/tests/test_validate_skill_consistency.py`

- [ ] **Step 1: Rewrite README around the fixed interface**

Lead with the product promise, then show: six inputs → three-axis planning → eight outputs → management/lawyer views → four task packages. State capability boundaries prominently. Keep concise example prompts and one sample management summary plus one task-package row.

- [ ] **Step 2: Update UI metadata**

Use:

```yaml
interface:
  display_name: "中国并购交易结构方案规划"
  short_description: "比较交易路径并输出双版本方案与后续任务包"
  default_prompt: "Use $handling-china-ma-transactions to plan this China M&A transaction structure from fixed inputs, compare a baseline, alternative, and fallback through 控制目标、路径比较、并表证据检验, and output management and lawyer views plus four downstream task packages."
```

- [ ] **Step 3: Run all unit tests**

```bash
python3 -m unittest discover -s scripts/tests -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit user-facing changes**

```bash
git add README.md skills/handling-china-ma-transactions/agents/openai.yaml skills/handling-china-ma-transactions/scripts/tests/test_validate_skill_consistency.py
git commit -m "docs: present structure planning skill"
```

### Task 6: Validate, forward-test, review, and deploy

**Files:**
- Modify as required by review findings.

- [ ] **Step 1: Run all deterministic validation**

```bash
python3 -m unittest discover -s scripts/tests -v
python3 scripts/validate_legal_authorities.py
python3 scripts/validate_skill_consistency.py
python3 /Users/zhanghongyang/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
git diff --check
```

Run from `skills/handling-china-ma-transactions` except `git diff --check`, which runs from the repository root. Expected: all commands succeed with no warnings or placeholder errors.

- [ ] **Step 2: Forward-test three raw scenarios with fresh agents**

Use only the revised Skill and raw scenario facts:

1. A-share control acquisition combining a share transfer and issuance, with one missing recommendation-blocker;
2. private-company staged control investment where consolidation evidence is incomplete;
3. asset/business acquisition where the user asks for a full SPA review, testing that the Skill returns a document task package rather than pretending to complete the review.

Check that each output uses six input groups, respects the gate, compares three paths or exclusions, produces both views, and creates only relevant task packages.

- [ ] **Step 3: Run independent product and architecture reviews**

Ask one reviewer to inspect legal-product boundaries and one to inspect Skill discoverability, fixed interfaces, and internal consistency. Fix Critical and Important findings with a new failing test before implementation.

- [ ] **Step 4: Re-run the entire validation suite after fixes**

Expected: all tests and validators pass from a clean working tree except intended commits.

- [ ] **Step 5: Commit final review fixes**

```bash
git add README.md skills/handling-china-ma-transactions docs/superpowers
git commit -m "fix: close structure planning review findings"
```

- [ ] **Step 6: Push the branch and update the installed copy**

Push the verified commits to the configured GitHub remote. Replace the installed `~/.codex/skills/handling-china-ma-transactions` copy only after repository validation passes, then run `quick_validate.py` against the installed copy.

