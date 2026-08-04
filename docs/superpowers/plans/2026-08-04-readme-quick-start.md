# README Quick-Start Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the repository README with a user-focused quick-start page that makes the China M&A Skill's capabilities, routing architecture, legal-authority controls and copyable usage immediately visible.

**Architecture:** Keep all user-facing orientation in the root `README.md`. Present the Skill as a transaction workflow rather than a file collection: matter intake and routing lead to layered legal/playbook sources, a fact-to-clause loop and defined deliverables. Retain installation, validation and legal-boundary warnings at the end.

**Tech Stack:** GitHub-flavored Markdown, Mermaid, Python 3 standard-library validation scripts, GitHub repository content API.

---

## File map

- Modify: `README.md` — user-facing landing page and quick-start guide.
- Read: `skills/handling-china-ma-transactions/SKILL.md` — canonical capabilities and routing rules.
- Read: `skills/handling-china-ma-transactions/references/legal-authorities.json` — current authority and audit counts.
- Test: `skills/handling-china-ma-transactions/scripts/tests/` — ensures README claims match a functioning Skill package.

### Task 1: Establish current facts and README acceptance checks

**Files:**

- Read: `README.md`
- Read: `skills/handling-china-ma-transactions/references/legal-authorities.json`
- Read: `skills/handling-china-ma-transactions/scripts/tests/`

- [ ] **Step 1: Record the current repository facts**

Run from the repository root:

```bash
python3 -c "import json; p='skills/handling-china-ma-transactions/references/legal-authorities.json'; d=json.load(open(p)); print(len(d['authorities']), d['registry_last_audited'])"
python3 -m unittest discover -s skills/handling-china-ma-transactions/scripts/tests -v
```

Expected: `44 2026-08-04` and 18 passing tests.

- [ ] **Step 2: Define deterministic README checks**

The final README must contain all of these exact anchors:

```text
什么时候使用
能力地图
L-CONTROL
P-EQUITY
P-ASSET
工作架构
现行硬法源
问题—条款闭环
可复制的使用示例
输出示例
passed_with_limitations
python3 scripts/validate_legal_authorities.py
```

The README must not contain `TODO`, `TBD`, `待补充`, unsupported market percentages or a claim that the Skill replaces lawyers, auditors or other professionals.

### Task 2: Rewrite the root README

**Files:**

- Modify: `README.md`

- [ ] **Step 1: Replace the existing README with the approved quick-start structure**

Write the following sections in this order:

```markdown
# Cross-border M&A Investment Skills

> 面向中国投资并购交易的 Codex Skill：从交易结构、法律尽调和条款谈判，一直工作到审批、交割与交割后事项。

中国法域 v1｜买方默认、卖方可切换｜44条版本化法源记录｜18项自动测试

## 什么时候使用

列出上市公司控制权收购、非上市公司股权收购、资产/业务收购、尽调到SPA闭环、审批交割、买卖方谈判及中国买方境外收购的中国侧工作流。

## 能力地图

用“能力／典型问题／主要输出”表格展示交易结构、尽调、文件条款、审批交割、谈判、控制与并表接口。

## 三条交易路由

用表格解释 L-CONTROL、P-EQUITY、P-ASSET，并注明真实混合交易才叠加路由。

## 工作架构

使用 Mermaid 展示：交易问题与材料 → 入项闸门 → 三条路由 → 法源与Playbook分层 → 问题—条款闭环 → 交付物 → 完成状态。

## 法源不是一个静态清单

用表格区分现行硬法源、监管/案例材料、历史/草案和市场Playbook；说明as-of、status_as_of、官方链接、同任务复核和MNPI搜索限制。

## 可复制的使用示例

提供五个完整中文指令：A股29%控制交易、非上市公司买方尽调、SPA审阅、卖方责任限制谈判、地方国企境外收购中国侧审批。

## 输出示例

展示事项元数据和一个许可到期Issue，包含事实、材料缺口、风险、主方案、fallback、owner、证据和状态。

## 安装

保留复制Skill目录及$handling-china-ma-transactions调用方式。

## 验证

保留unittest、法源校验和一致性校验三条命令。

## 使用边界

保留法源核验日、专业意见、外国法和MNPI边界。
```

Every section must use concise finished prose rather than the planning descriptions above. Keep the Mermaid graph to one screen and use no more than three tables before the examples.

- [ ] **Step 2: Verify the README content contract**

Run:

```bash
rg -n "什么时候使用|能力地图|L-CONTROL|P-EQUITY|P-ASSET|工作架构|现行硬法源|问题—条款闭环|可复制的使用示例|输出示例|passed_with_limitations|validate_legal_authorities" README.md
! rg -n "TODO|TBD|待补充" README.md
```

Expected: every required anchor is printed by the first command; the second command returns no match.

### Task 3: Validate and publish

**Files:**

- Test: `README.md`
- Test: `skills/handling-china-ma-transactions/scripts/tests/`

- [ ] **Step 1: Run the Skill package checks from the repository copy**

Run:

```bash
cd skills/handling-china-ma-transactions
python3 -m unittest discover -s scripts/tests -v
python3 scripts/validate_legal_authorities.py
python3 scripts/validate_skill_consistency.py
```

Expected: 18 tests pass and both validators print `OK`.

- [ ] **Step 2: Inspect the final README diff**

Confirm the diff changes only `README.md` for the user-facing implementation; the already-approved design and plan documents are separate documentation commits.

- [ ] **Step 3: Publish the README update**

Update root `README.md` on `main` with commit message:

```text
Improve China M&A skill quick start
```

- [ ] **Step 4: Verify the remote file**

Fetch `README.md` from `main` and confirm it contains `能力地图`, the Mermaid `flowchart`, all three route codes and `可复制的使用示例`.
