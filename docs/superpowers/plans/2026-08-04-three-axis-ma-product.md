# China M&A Three-Axis Product Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reframe `handling-china-ma-transactions` as a China M&A decision-and-execution Skill whose mandatory core is control, acquisition method and financial-statement consolidation.

**Architecture:** Keep `SKILL.md` concise and make it route every transaction through a new three-axis engine reference. Add one integrated output asset containing the three required matrices, then make diligence, approvals, negotiation and closing explicitly map back to the axes. Extend the existing consistency validator and unit tests so the product contract is mechanically enforced.

**Tech Stack:** Markdown Skill instructions and assets, Python 3 standard-library validators/tests, Git, Codex subagent forward evaluation.

---

## File map

- Create `skills/handling-china-ma-transactions/references/three-axis-transaction-engine.md`: authoritative workflow for the three-axis reasoning kernel and route adaptations.
- Create `skills/handling-china-ma-transactions/assets/three-axis-structure-template.md`: integrated control, acquisition-method and consolidation matrices.
- Modify `skills/handling-china-ma-transactions/SKILL.md`: product definition, mandatory three-axis sequence and direct links.
- Modify `skills/handling-china-ma-transactions/references/output-contract.md`: three-axis minimum outputs and execution-layer mapping.
- Modify `skills/handling-china-ma-transactions/references/listed-control.md`: explicitly consume and populate the three-axis engine.
- Modify `skills/handling-china-ma-transactions/references/accounting-control-and-consolidation.md`: define inputs from the first two axes and outputs to execution.
- Modify `skills/handling-china-ma-transactions/assets/matter-intake-template.md`: capture the three target states at intake.
- Modify `skills/handling-china-ma-transactions/assets/due-diligence-issue-list-template.md`: add affected-axis mapping.
- Modify `skills/handling-china-ma-transactions/assets/approval-matrix-template.md`: add affected-axis mapping.
- Modify `skills/handling-china-ma-transactions/assets/negotiation-plan-template.md`: add affected-axis mapping.
- Modify `skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py`: enforce the product contract and new resources.
- Modify `skills/handling-china-ma-transactions/scripts/tests/test_validate_skill_consistency.py`: test the new validator behavior first.
- Modify `skills/handling-china-ma-transactions/agents/openai.yaml`: align UI metadata and default prompt with the product.
- Modify `README.md`: lead with the product definition and three-axis architecture.

### Task 1: Establish failing product-contract tests

**Files:**
- Modify: `skills/handling-china-ma-transactions/scripts/tests/test_validate_skill_consistency.py`
- Modify: `skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py`

- [ ] **Step 1: Run a baseline forward evaluation on the current Skill**

Ask an independent agent to use the current Skill on an A-share control-acquisition scenario without disclosing the expected three-axis answer. Save only the assessment in the task notes; do not add the agent output to the repository.

Expected baseline weakness: control, acquisition method and consolidation may appear, but are not guaranteed to be presented as a mandatory linked decision sequence with three matrices.

- [ ] **Step 2: Write tests for the missing product contract**

Add the following tests:

```python
def test_three_axis_product_contract_is_enforced(self):
    spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    self.assertEqual(module.validate_skill(ROOT), [])


def test_validator_rejects_missing_three_axis_product_language(self):
    spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory() as temp_dir:
        copied_root = Path(temp_dir) / "skill"
        shutil.copytree(ROOT, copied_root)
        skill = copied_root / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace("三维决策内核", "交易分析框架"),
            encoding="utf-8",
        )
        errors = module.validate_skill(copied_root)
    self.assertIn("SKILL.md lacks three-axis product contract: 三维决策内核", errors)
```

- [ ] **Step 3: Add validator requirements before adding production content**

Require these elements:

```python
THREE_AXIS_SKILL_TOKENS = (
    "中国投资并购决策与执行 Skill",
    "三维决策内核",
    "控制权",
    "收购方式",
    "合并财务报表",
)

THREE_AXIS_ASSET_SECTIONS = (
    "控制权矩阵",
    "收购方式比较矩阵",
    "并表支持与证据矩阵",
    "跨维度依赖",
)
```

Also require a direct Skill link to the new reference and asset, three-axis language in the output contract, and an `影响维度` field in the diligence, approval and negotiation templates.

- [ ] **Step 4: Run the focused tests and verify RED**

Run:

```bash
python3 -m unittest skills.handling-china-ma-transactions.scripts.tests.test_validate_skill_consistency -v
```

If module-path discovery is unsuitable because the skill directory contains hyphens, run:

```bash
python3 -m unittest discover -s skills/handling-china-ma-transactions/scripts/tests -p 'test_validate_skill_consistency.py' -v
```

Expected: FAIL because the current Skill lacks the new product language, reference and asset.

- [ ] **Step 5: Commit the failing tests**

```bash
git add skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py skills/handling-china-ma-transactions/scripts/tests/test_validate_skill_consistency.py
git commit -m "Test three-axis M&A product contract"
```

### Task 2: Implement the three-axis kernel and integrated template

**Files:**
- Create: `skills/handling-china-ma-transactions/references/three-axis-transaction-engine.md`
- Create: `skills/handling-china-ma-transactions/assets/three-axis-structure-template.md`
- Modify: `skills/handling-china-ma-transactions/SKILL.md`
- Modify: `skills/handling-china-ma-transactions/references/output-contract.md`

- [ ] **Step 1: Write the three-axis reference**

Define:

- the product promise and start→means→target chain;
- mandatory execution for `L-CONTROL`;
- explicit `not-sought`, `not-applicable` or `pending-professional-confirmation` states for `P-EQUITY` and `P-ASSET`;
- control facts and counter-evidence;
- at least three acquisition structures when facts permit, or elimination reasons;
- consolidation support, counter-evidence, purchase-date timeline and auditor confirmation package;
- execution-layer mapping for diligence, approvals, terms, negotiation and closing;
- conditional conclusions and professional boundaries.

- [ ] **Step 2: Add the integrated template**

Include common matter metadata followed by:

```markdown
## 三维执行摘要
## 第一维：控制权矩阵
## 第二维：收购方式比较矩阵
## 第三维：并表支持与证据矩阵
## 跨维度依赖
## 推荐方案、Fallback 与行动清单
```

The acquisition-method table must compare control result, approvals, funds/cost, timeline, dependencies, failure consequences, recovery and consolidation support.

- [ ] **Step 3: Reorder the Skill around the product kernel**

Place the product definition and three-axis workflow after the core rules and matter intake. Keep route selection and progressive disclosure, but state that lifecycle modules support rather than replace the kernel. Directly link the new reference and asset.

- [ ] **Step 4: Strengthen the output contract**

Require structure memoranda to use the integrated template, compare three structures when facts permit and explain eliminated routes when fewer remain. Require non-structure tasks to state their affected axes without fabricating a full structure memo.

- [ ] **Step 5: Run focused tests and verify GREEN**

```bash
python3 -m unittest discover -s skills/handling-china-ma-transactions/scripts/tests -p 'test_validate_skill_consistency.py' -v
python3 skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py
```

Expected: PASS and `OK: skill references, assets, routes and metadata are consistent`.

- [ ] **Step 6: Commit the kernel**

```bash
git add skills/handling-china-ma-transactions/SKILL.md skills/handling-china-ma-transactions/references/three-axis-transaction-engine.md skills/handling-china-ma-transactions/references/output-contract.md skills/handling-china-ma-transactions/assets/three-axis-structure-template.md
git commit -m "Add three-axis M&A decision kernel"
```

### Task 3: Connect execution modules to the three axes

**Files:**
- Modify: `skills/handling-china-ma-transactions/references/listed-control.md`
- Modify: `skills/handling-china-ma-transactions/references/accounting-control-and-consolidation.md`
- Modify: `skills/handling-china-ma-transactions/assets/matter-intake-template.md`
- Modify: `skills/handling-china-ma-transactions/assets/due-diligence-issue-list-template.md`
- Modify: `skills/handling-china-ma-transactions/assets/approval-matrix-template.md`
- Modify: `skills/handling-china-ma-transactions/assets/negotiation-plan-template.md`

- [ ] **Step 1: Add three target states to intake**

Capture:

```markdown
## 三维目标

| 维度 | 目标状态 | 必须实现的商业结果 | 不可接受结果 | 最终确认人 |
|---|---|---|---|---|
| 控制权 |  |  |  |  |
| 收购方式 |  |  |  |  |
| 合并财务报表 |  |  |  |  |
```

- [ ] **Step 2: Add affected-axis fields to execution templates**

Add an `影响维度` column to the diligence, approval and negotiation primary tables. The field accepts one or more of `控制权 / 收购方式 / 合并财务报表` and requires a short causal explanation where the link is not obvious.

- [ ] **Step 3: Align listed-control and consolidation references**

Make `listed-control.md` populate the first two axes and feed the third; keep route-specific offer, issuance, voting, governance and transition rules. Make the consolidation reference declare required inputs from the first two axes and return support facts, counter-evidence, purchase-date candidates and auditor evidence.

- [ ] **Step 4: Run tests and validators**

```bash
python3 -m unittest discover -s skills/handling-china-ma-transactions/scripts/tests -v
python3 skills/handling-china-ma-transactions/scripts/validate_legal_authorities.py
python3 skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py
```

Expected: all tests and both validators pass.

- [ ] **Step 5: Commit the execution-layer integration**

```bash
git add skills/handling-china-ma-transactions/references/listed-control.md skills/handling-china-ma-transactions/references/accounting-control-and-consolidation.md skills/handling-china-ma-transactions/assets/matter-intake-template.md skills/handling-china-ma-transactions/assets/due-diligence-issue-list-template.md skills/handling-china-ma-transactions/assets/approval-matrix-template.md skills/handling-china-ma-transactions/assets/negotiation-plan-template.md
git commit -m "Map M&A execution layers to three axes"
```

### Task 4: Present and forward-test the product

**Files:**
- Modify: `README.md`
- Modify: `skills/handling-china-ma-transactions/agents/openai.yaml`

- [ ] **Step 1: Rewrite the README opening and architecture**

Lead with this product category:

```text
中国投资并购决策与执行 Skill
```

Show the three-axis engine before the capability map. Explain that diligence, approvals, clauses, negotiation and closing are execution layers, and retain quick-start prompts and current scope boundaries.

- [ ] **Step 2: Align UI metadata**

Update `short_description` and `default_prompt` so the Skill is presented as a transaction decision-and-execution product and the default prompt asks for the three-axis analysis.

- [ ] **Step 3: Run post-change forward evaluations**

Use fresh agents on at least:

1. an A-share 29% agreement-transfer plus issuance scenario seeking control and consolidation;
2. a pure private minority financing that does not seek control, business or assets;
3. an asset/business acquisition where the accounting perimeter needs professional confirmation.

Do not reveal expected answers. Verify that outputs explicitly handle all three axes, use `not-sought` and hand off the pure minority financing to the PE/VC skill, use `pending-professional-confirmation` for the asset/accounting-perimeter scenario and map execution actions back to the affected axis.

- [ ] **Step 4: Run full verification**

```bash
python3 -m unittest discover -s skills/handling-china-ma-transactions/scripts/tests -v
python3 skills/handling-china-ma-transactions/scripts/validate_legal_authorities.py
python3 skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py
python3 /Users/zhanghongyang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/handling-china-ma-transactions
git diff --check origin/main...HEAD
```

Expected: all tests and validators pass; no whitespace errors.

- [ ] **Step 5: Request independent review and fix material findings**

Provide reviewers the design spec, base SHA, head SHA and raw diff. Request separate product/spec and quality/risk reviews. Fix Critical and Important findings, then rerun full verification.

- [ ] **Step 6: Commit presentation changes**

```bash
git add README.md skills/handling-china-ma-transactions/agents/openai.yaml
git commit -m "Present three-axis China M&A Skill"
```

### Task 5: Publish and synchronize deliverables

**Files:**
- Synchronize: `/Users/zhanghongyang/Documents/Codex/2026-08-04/w-x/outputs/Cross-border-M-and-A-Investment`
- Synchronize: `/Users/zhanghongyang/.codex/skills/handling-china-ma-transactions`

- [ ] **Step 1: Verify intended Git scope**

```bash
git status -sb
git diff --stat origin/main...HEAD
git log --oneline origin/main..HEAD
```

Confirm only the product spec, plan and intended Skill/README files changed.

- [ ] **Step 2: Publish the reviewed commit set to GitHub `main`**

Use the authenticated GitHub connector if local GitHub CLI authentication is unavailable. Update `main` only after all checks pass and verify the remote head SHA.

- [ ] **Step 3: Synchronize the output and installed copies**

Copy the reviewed repository files to the user-facing output directory and the reviewed Skill folder to the personal installation, preserving unrelated files. Verify file hashes for all changed files.

- [ ] **Step 4: Rerun verification against the synchronized Skill**

```bash
python3 -m unittest discover -s /Users/zhanghongyang/.codex/skills/handling-china-ma-transactions/scripts/tests -v
python3 /Users/zhanghongyang/.codex/skills/handling-china-ma-transactions/scripts/validate_legal_authorities.py
python3 /Users/zhanghongyang/.codex/skills/handling-china-ma-transactions/scripts/validate_skill_consistency.py
```

Expected: all tests and validators pass from the installed copy.
