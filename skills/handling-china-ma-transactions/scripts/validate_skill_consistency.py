#!/usr/bin/env python3
"""Validate cross-file invariants for the China M&A skill."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ASSET_RE = re.compile(r"assets/([A-Za-z0-9_.-]+)")
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|placeholder)\b|待补(?:充|写)?", re.IGNORECASE)

COMMON_ASSET_FIELDS = (
    "事项：",
    "路由：",
    "立场：",
    "As-of / 法律核验日：",
    "材料范围 / 版本：",
    "关键假设：",
    "法域：",
    "完成状态：",
)

TRANSACTION_ROUTES = ("L-CONTROL", "P-EQUITY", "P-ASSET")

THREE_AXIS_SKILL_TOKENS = (
    "三维决策内核",
    "控制权",
    "收购方式",
    "合并财务报表",
)

PRODUCT_POSITIONING = "交易结构方案规划"

FIXED_INPUT_GROUPS = (
    "事项信息",
    "商业目标",
    "交易事实",
    "可选路径",
    "硬约束",
    "材料与缺口",
)
FIELD_REQUIREMENT_LEVELS = (
    "start-required",
    "assumption-allowed",
    "recommendation-blocker",
)
FACT_STATUSES = (
    "confirmed",
    "assumed",
    "missing",
    "conflicting",
    "external-confirmation-pending",
)
INPUT_TRACKING_FIELDS = (
    "要求等级",
    "事实状态",
    "对方案的影响",
    "责任人",
    "关闭证据",
)

FIXED_OUTPUT_SECTIONS = (
    "项目状态及分析边界",
    "一页式方案结论",
    "三维目标及当前状态",
    "基准、备选、兜底三个方案比较",
    "推荐方案、推荐理由及成立条件",
    "关键反证、缺失事实和待决策事项",
    "签署—审批—交割—控制取得—并表判断时间线",
    "后续任务包",
)
DELIVERY_VIEWS = ("管理层决策版", "律师执行版")
DELIVERY_SHARED_FIELDS = (
    "方案 ID",
    "关键事实",
    "状态",
    "推荐结论",
    "时间线",
)
DELIVERY_CONSISTENCY_RULE = (
    "两个版本的方案编号、关键事实、状态、推荐结论和时间线必须一致"
)

DOWNSTREAM_TASK_PACKAGES_ASSET = "assets/downstream-task-packages-template.md"
DOWNSTREAM_TASK_PACKAGES = (
    "尽调任务包",
    "交易文件任务包",
    "审批任务包",
    "会计任务包",
)
DOWNSTREAM_TASK_PACKAGE_FIELDS = (
    "Package ID",
    "接收方",
    "来源方案/维度",
    "目的",
    "待核事实/待完成动作",
    "输入材料",
    "问题或指令",
    "责任人",
    "期限/阶段",
    "完成证据",
    "结果回传字段",
    "状态",
)

FORBIDDEN_CAPABILITY_CLAIMS = frozenset(
    (
        "- **法律尽职调查**：红旗尽调、完整尽调、Major Issues、更新尽调及问题—条款映射；",
        "- **交易文件与谈判**：SPA/APA、股份转让或认购协议、披露、保证、赔偿、责任限制和交割机制；",
        "- **审批与交割**：经营者集中、国资、外资准入、安全审查、ODI/外汇、数据、技术出口和出口管制；",
        "description: Use when advising on China-focused investment or M&A transactions, including legal due diligence, transaction structuring, listed-company control acquisitions, private share or asset purchases, SPA/APA terms, regulatory approvals, signing or closing, negotiation, and buyer- or seller-side issue analysis.",
        "- Use the three-axis kernel before working the lifecycle: structure → contact/NDA → diligence → documents/negotiation → signing → effectiveness/approvals → closing → post-closing/integration → claims.",
        'short_description: "以三维决策内核驱动中国并购结构与执行"',
        'default_prompt: "Use $handling-china-ma-transactions from the buyer perspective. For structure requests, analyze 控制权、收购方式、合并财务报表 in that causal order as the 三维 decision kernel, then map diligence, approvals, terms, negotiation and closing actions to the affected axes. For non-structure requests, identify only the affected axes and do not fabricate a full transaction structure."',
        "| 法律尽调 | 完整尽调与 Major Issues |",
        "| SPA审阅 | 审阅交易文件并输出红线 |",
        "| 整合 | 输出 100 日整合计划 |",
        "| 索赔 | 执行索赔管理 |",
        "本 Skill 可输出完整尽调报告",
        "本 Skill 可完成整套交易文件起草",
        "本 Skill 可审阅 SPA",
        "本 Skill 可执行全议题谈判",
        "本 Skill 可完成审批申报",
        "本 Skill 可执行申报",
        "本 Skill 可输出会计结论",
        "本 Skill 可负责交割管理",
        "本 Skill 可输出整合计划",
        "本 Skill 可执行索赔",
    )
)

THREE_AXIS_REFERENCE = "references/three-axis-transaction-engine.md"
THREE_AXIS_ASSET = "assets/three-axis-structure-template.md"
THREE_AXIS_CAUSAL_SEQUENCE = (
    "先确定控制权目标",
    "围绕控制目标生成和比较路径",
    "从前两维提取",
)
P_ASSET_ACCOUNTING_TOKENS = (
    "P-ASSET 分支：资产边界与经营主导权",
    "P-ASSET 分支：资产收购或业务合并",
    "投入与实质性加工处理过程",
    "集中度测试",
    "确认日 / 购买日",
)
PRIVATE_ROUTE_PATH_CONTRACT = (
    "事实允许时至少比较三个方案；不足三个时列明被排除路径及原因"
)

START_GATE_RE = re.compile(r"`start-required`[^。\n]*缺失时[^。\n]*不能启动")
RECOMMENDATION_GATE_RE = re.compile(
    r"`recommendation-blocker`[^。\n]*可以比较路径[^。\n]*缺失时"
    r"[^。\n]*不得给出确定推荐[^。\n]*`blocked`"
)
NON_CONFIRMED_CLOSURE_RE = re.compile(
    r"每一非\s*`confirmed`\s*项[^。\n]*对方案的影响[^。\n]*责任人[^。\n]*关闭证据"
)


def _find_heading(text: str, title: str):
    return re.search(
        rf"^#{{1,6}}\s+(?:\d+(?:\.\d+)*[.、]?\s+)?{re.escape(title)}\s*$",
        text,
        re.MULTILINE,
    )


def _find_numbered_heading(text: str, index: int, title: str):
    return re.search(
        rf"^#{{1,6}}\s+{index}[.、]\s+{re.escape(title)}\s*$",
        text,
        re.MULTILINE,
    )


def _find_numbered_entry(text: str, index: int, title: str):
    patterns = (
        rf"^#{{1,6}}\s+{index}[.、]\s+{re.escape(title)}\s*$",
        rf"^{index}[.、]\s+(?:\*\*)?{re.escape(title)}(?:\*\*)?(?:[：:].*)?$",
        rf"^\|\s*{index}\s*\|\s*(?:\*\*)?{re.escape(title)}(?:\*\*)?\s*\|",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match is not None:
            return match
    return None


def _extract_heading_section(text: str, title: str) -> str:
    heading = _find_heading(text, title)
    if heading is None:
        return ""
    level = len(heading.group(0)) - len(heading.group(0).lstrip("#"))
    next_heading = re.search(
        rf"^#{{1,{level}}}\s+", text[heading.end() :], re.MULTILINE
    )
    end = heading.end() + next_heading.start() if next_heading else len(text)
    return text[heading.end() : end]


def _table_rows(text: str):
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = tuple(cell.strip().strip("`") for cell in stripped[1:-1].split("|"))
        if cells and not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            rows.append(cells)
    return rows


def _validate_overclaims(path: Path, label: str) -> List[str]:
    errors = []
    if not path.exists():
        return errors
    for line in path.read_text(encoding="utf-8").splitlines():
        claim = line.strip()
        if claim in FORBIDDEN_CAPABILITY_CLAIMS:
            errors.append(f"downstream overclaim in {label}: {claim}")
    return errors


def _validate_internal_links(path: Path, root: Path) -> List[str]:
    errors: List[str] = []
    for target in LINK_RE.findall(path.read_text(encoding="utf-8")):
        target = target.strip().strip("<>")
        if not target or target.startswith("#") or "://" in target:
            continue
        local_target = target.split("#", 1)[0]
        if not local_target:
            continue
        if not (path.parent / local_target).exists():
            errors.append(
                f"broken internal link in {path.relative_to(root).as_posix()}: "
                f"{local_target}"
            )
    return errors


def validate_skill(root: Path) -> List[str]:
    errors: List[str] = []
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        return ["SKILL.md is missing"]

    skill = skill_path.read_text(encoding="utf-8")
    lines = skill.splitlines()
    if len(lines) > 300:
        errors.append(f"SKILL.md has {len(lines)} lines; maximum is 300")
    if "name: handling-china-ma-transactions" not in skill:
        errors.append("SKILL.md frontmatter name is missing or incorrect")
    if "Perspective: Buyer" not in skill or "Perspective: Seller" not in skill:
        errors.append("SKILL.md must declare both perspective labels")

    for token in THREE_AXIS_SKILL_TOKENS:
        if token not in skill:
            errors.append(f"SKILL.md lacks three-axis product contract: {token}")
    if PRODUCT_POSITIONING not in skill:
        errors.append(f"SKILL.md lacks product positioning: {PRODUCT_POSITIONING}")

    required_tokens = {
        "L-CONTROL",
        "P-EQUITY",
        "P-ASSET",
        "passed",
        "passed_with_limitations",
        "blocked",
        "do not search for, quote, calculate or state foreign filing thresholds",
    }
    for token in sorted(required_tokens):
        if token not in skill:
            errors.append(f"SKILL.md does not route required token: {token}")

    links = {target.split("#", 1)[0] for target in LINK_RE.findall(skill)}
    references_dir = root / "references"
    if not (root / THREE_AXIS_REFERENCE).exists():
        errors.append(
            f"required three-axis reference is missing: {THREE_AXIS_REFERENCE}"
        )
    else:
        three_axis_reference = (root / THREE_AXIS_REFERENCE).read_text(
            encoding="utf-8"
        )
        causal_positions = []
        for token in THREE_AXIS_CAUSAL_SEQUENCE:
            position = three_axis_reference.find(token)
            if position < 0:
                errors.append(f"three-axis reference breaks causal sequence: {token}")
            else:
                causal_positions.append(position)
        if len(causal_positions) == len(THREE_AXIS_CAUSAL_SEQUENCE) and (
            causal_positions != sorted(causal_positions)
        ):
            errors.append("three-axis reference causal sequence is out of order")
    three_axis_asset = ""
    if not (root / THREE_AXIS_ASSET).exists():
        errors.append(f"required three-axis asset is missing: {THREE_AXIS_ASSET}")
    else:
        three_axis_asset = (root / THREE_AXIS_ASSET).read_text(encoding="utf-8")
        output_positions = []
        for section in FIXED_OUTPUT_SECTIONS:
            match = _find_heading(three_axis_asset, section)
            if match is None:
                errors.append(
                    f"three-axis asset lacks fixed output section: {section}"
                )
            else:
                output_positions.append(match.start())
        if output_positions != sorted(output_positions):
            errors.append("three-axis asset fixed output sections are out of order")

        for view in DELIVERY_VIEWS:
            view_section = _extract_heading_section(three_axis_asset, view)
            if not view_section:
                errors.append(f"three-axis asset lacks delivery view: {view}")
                continue
            rows = _table_rows(view_section)
            if not any(all(field in row for field in DELIVERY_SHARED_FIELDS) for row in rows):
                errors.append(
                    f"three-axis asset delivery view {view} lacks shared fields"
                )

    for path in sorted(references_dir.glob("*.md")):
        relative = path.relative_to(root).as_posix()
        if relative not in links:
            errors.append(f"reference not directly linked from SKILL.md: {relative}")
    registry_relative = "references/legal-authorities.json"
    if (root / registry_relative).exists() and registry_relative not in links:
        errors.append("legal authority registry is not directly linked from SKILL.md")

    output_contract = references_dir / "output-contract.md"
    if output_contract.exists():
        contract_text = output_contract.read_text(encoding="utf-8")
        contract_positions = []
        for index, section in enumerate(FIXED_OUTPUT_SECTIONS, start=1):
            match = re.search(
                rf"^(?:#{{1,6}}\s+)?{index}[.、]\s+(?:\*\*)?"
                rf"{re.escape(section)}(?:\*\*)?(?:[：:；;。].*)?$",
                contract_text,
                re.MULTILINE,
            )
            if match is None:
                errors.append(f"output contract lacks fixed output section: {section}")
            else:
                contract_positions.append(match.start())
        if contract_positions != sorted(contract_positions):
            errors.append("output contract fixed output sections are out of order")

        for view in DELIVERY_VIEWS:
            if view not in contract_text:
                errors.append(f"output contract lacks delivery view: {view}")
        if "同一底层分析" not in contract_text:
            errors.append("output contract lacks shared-analysis rule: 同一底层分析")
        if DELIVERY_CONSISTENCY_RULE not in contract_text:
            errors.append("output contract lacks delivery-view consistency rule")
        for asset_name in sorted(set(ASSET_RE.findall(contract_text))):
            if not (root / "assets" / asset_name).exists():
                errors.append(f"asset named by output contract is missing: assets/{asset_name}")
    else:
        errors.append("required output contract is missing: references/output-contract.md")

    for path in sorted((root / "assets").glob("*.md")):
        relative = path.relative_to(root).as_posix()
        if relative not in links:
            errors.append(f"asset not directly linked from SKILL.md: {relative}")
        asset_text = path.read_text(encoding="utf-8")
        for field in COMMON_ASSET_FIELDS:
            if field not in asset_text:
                errors.append(f"asset lacks common matter field {field}: {relative}")
        for route in TRANSACTION_ROUTES:
            if route not in asset_text:
                errors.append(f"asset lacks transaction route {route}: {relative}")

    intake = root / "assets" / "matter-intake-template.md"
    if not intake.exists():
        errors.append("required matter intake asset is missing: assets/matter-intake-template.md")
    else:
        intake_text = intake.read_text(encoding="utf-8")
        if "三维目标" not in intake_text:
            errors.append("matter intake lacks three-axis target states: 三维目标")

        intake_positions = []
        for index, group in enumerate(FIXED_INPUT_GROUPS, start=1):
            heading = _find_numbered_heading(intake_text, index, group)
            if heading is None:
                errors.append(f"matter intake lacks fixed input group: {group}")
                continue
            intake_positions.append(heading.start())
            if not _table_rows(_extract_heading_section(intake_text, group)):
                errors.append(f"matter intake group lacks field table: {group}")
        if intake_positions != sorted(intake_positions):
            errors.append("matter intake fixed input groups are out of order")

        for level in FIELD_REQUIREMENT_LEVELS:
            if level not in intake_text:
                errors.append(f"matter intake lacks requirement level: {level}")
        for status in FACT_STATUSES:
            if status not in intake_text:
                errors.append(f"matter intake lacks fact status: {status}")
        if not any(
            all(field in row for field in INPUT_TRACKING_FIELDS)
            for row in _table_rows(intake_text)
        ):
            errors.append(
                "matter intake does not separate requirement levels, fact statuses "
                "and closure fields"
            )

    intake_reference = references_dir / "intake-routing-and-gates.md"
    if not intake_reference.exists():
        errors.append(
            "required intake reference is missing: references/intake-routing-and-gates.md"
        )
    else:
        intake_reference_text = intake_reference.read_text(encoding="utf-8")
        reference_positions = []
        for index, group in enumerate(FIXED_INPUT_GROUPS, start=1):
            entry = _find_numbered_entry(intake_reference_text, index, group)
            if entry is None:
                errors.append(f"intake reference lacks fixed input group: {group}")
            else:
                reference_positions.append(entry.start())
        if reference_positions != sorted(reference_positions):
            errors.append("intake reference fixed input groups are out of order")

        for level in FIELD_REQUIREMENT_LEVELS:
            if level not in intake_reference_text:
                errors.append(f"intake reference lacks requirement level: {level}")
        for status in FACT_STATUSES:
            if status not in intake_reference_text:
                errors.append(f"intake reference lacks fact status: {status}")
        if "要求等级与事实状态分开记录" not in intake_reference_text:
            errors.append("intake reference does not separate requirement levels and fact statuses")
        if not START_GATE_RE.search(intake_reference_text):
            errors.append("intake reference lacks start-required gate semantics")
        if not RECOMMENDATION_GATE_RE.search(intake_reference_text):
            errors.append("intake reference lacks recommendation-blocker gate semantics")
        if not NON_CONFIRMED_CLOSURE_RE.search(intake_reference_text):
            errors.append("intake reference lacks non-confirmed fact closure semantics")

    task_packages = root / DOWNSTREAM_TASK_PACKAGES_ASSET
    if DOWNSTREAM_TASK_PACKAGES_ASSET not in links:
        errors.append("downstream task packages template is not directly linked from SKILL.md")
    if not task_packages.exists():
        errors.append(
            "required downstream task packages template is missing: "
            f"{DOWNSTREAM_TASK_PACKAGES_ASSET}"
        )
    else:
        task_packages_text = task_packages.read_text(encoding="utf-8")
        package_positions = []
        for package in DOWNSTREAM_TASK_PACKAGES:
            heading = _find_heading(task_packages_text, package)
            if heading is None:
                errors.append(
                    "downstream task packages template lacks package section: "
                    f"{package}"
                )
                continue
            package_positions.append(heading.start())
            rows = _table_rows(_extract_heading_section(task_packages_text, package))
            schema = max(
                rows,
                key=lambda row: sum(
                    field in row for field in DOWNSTREAM_TASK_PACKAGE_FIELDS
                ),
                default=(),
            )
            for field in DOWNSTREAM_TASK_PACKAGE_FIELDS:
                if field not in schema:
                    errors.append(
                        f"downstream task package {package} lacks required field: {field}"
                    )
            if all(field in schema for field in DOWNSTREAM_TASK_PACKAGE_FIELDS):
                positions = [schema.index(field) for field in DOWNSTREAM_TASK_PACKAGE_FIELDS]
                if positions != sorted(positions):
                    errors.append(
                        f"downstream task package {package} fields are out of order"
                    )
        if package_positions != sorted(package_positions):
            errors.append("downstream task package sections are out of order")

    listed_control = references_dir / "listed-control.md"
    if listed_control.exists() and "三维内核接口" not in listed_control.read_text(
        encoding="utf-8"
    ):
        errors.append(
            "listed-control.md lacks three-axis route interface: 三维内核接口"
        )

    accounting = references_dir / "accounting-control-and-consolidation.md"
    if accounting.exists():
        accounting_text = accounting.read_text(encoding="utf-8")
        if "前两维输入" not in accounting_text:
            errors.append(
                "accounting reference lacks three-axis input contract: 前两维输入"
            )
        for token in P_ASSET_ACCOUNTING_TOKENS:
            if token not in accounting_text or token not in three_axis_asset:
                errors.append(f"P-ASSET accounting contract lacks route token: {token}")

    for filename in ("private-equity-ma.md", "private-asset-ma.md"):
        path = references_dir / filename
        if path.exists() and PRIVATE_ROUTE_PATH_CONTRACT not in path.read_text(
            encoding="utf-8"
        ):
            errors.append(
                f"{filename} lacks three-path structure contract: "
                f"{PRIVATE_ROUTE_PATH_CONTRACT}"
            )

    article_path = references_dir / "article-and-deal-seeds.md"
    if article_path.exists():
        article = article_path.read_text(encoding="utf-8")
        required_warnings = [
            "非现行硬法源",
            "2018投票权委托征求意见",
            "旧《公司法》第141条",
            "2026年7月再融资征求意见稿",
        ]
        for warning in required_warnings:
            if warning not in article:
                errors.append(f"article digest lacks stale-source warning: {warning}")

    registry = references_dir / "legal-authorities.json"
    if registry.exists():
        try:
            payload = json.loads(registry.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"legal authority registry cannot be read: {exc}")
        else:
            coverage_topics = set(payload.get("coverage_topics", []))
            matrix = payload.get("coverage_matrix", {})
            matrix_text = json.dumps(matrix, ensure_ascii=False)
            for topic in sorted(coverage_topics):
                if topic not in matrix_text:
                    errors.append(f"authority topic lacks a coverage-matrix route: {topic}")

    yaml_path = root / "agents" / "openai.yaml"
    if not yaml_path.exists():
        errors.append("agents/openai.yaml is missing")
    else:
        yaml_text = yaml_path.read_text(encoding="utf-8")
        if "$handling-china-ma-transactions" not in yaml_text:
            errors.append("openai.yaml default_prompt must mention the skill explicitly")
        if PRODUCT_POSITIONING not in yaml_text:
            errors.append(f"openai.yaml lacks product positioning: {PRODUCT_POSITIONING}")

    readme_path = root.parents[1] / "README.md"
    if readme_path.exists():
        if PRODUCT_POSITIONING not in readme_path.read_text(encoding="utf-8"):
            errors.append(f"README.md lacks product positioning: {PRODUCT_POSITIONING}")

    for path, label in (
        (skill_path, "SKILL.md"),
        (readme_path, "README.md"),
        (yaml_path, "agents/openai.yaml"),
    ):
        errors.extend(_validate_overclaims(path, label))

    for path in [skill_path, *references_dir.glob("*.md"), *(root / "assets").glob("*.md")]:
        errors.extend(_validate_internal_links(path, root))
        match = PLACEHOLDER_RE.search(path.read_text(encoding="utf-8"))
        if match:
            errors.append(f"placeholder text in {path.relative_to(root)}: {match.group(0)}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_skill(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: skill references, assets, routes and metadata are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
