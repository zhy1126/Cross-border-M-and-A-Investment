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

LISTED_CONTROL_COVERAGE = (
    "公开资料",
    "MNPI",
    "股份转让协议",
    "股份认购协议",
    "要约",
    "权益变动",
    "表决权",
    "治理",
    "法定或监管硬门不得以合同约定豁免",
)

THREE_AXIS_SKILL_TOKENS = (
    "中国投资并购决策与执行 Skill",
    "三维决策内核",
    "控制权",
    "收购方式",
    "合并财务报表",
)

THREE_AXIS_REFERENCE = "references/three-axis-transaction-engine.md"
THREE_AXIS_ASSET = "assets/three-axis-structure-template.md"
THREE_AXIS_ASSET_SECTIONS = (
    "三维执行摘要",
    "控制权矩阵",
    "收购方式比较矩阵",
    "并表支持与证据矩阵",
    "跨维度依赖",
)
THREE_AXIS_OUTPUT_TOKENS = (
    "三维执行摘要",
    "控制权矩阵",
    "收购方式比较矩阵",
    "并表支持与证据矩阵",
    "至少三个",
    "排除原因",
)
THREE_AXIS_EXECUTION_ASSETS = (
    "approval-matrix-template.md",
    "due-diligence-issue-list-template.md",
    "negotiation-plan-template.md",
)


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
    if not (root / THREE_AXIS_ASSET).exists():
        errors.append(f"required three-axis asset is missing: {THREE_AXIS_ASSET}")
    else:
        three_axis_asset = (root / THREE_AXIS_ASSET).read_text(encoding="utf-8")
        for section in THREE_AXIS_ASSET_SECTIONS:
            if section not in three_axis_asset:
                errors.append(
                    f"three-axis asset lacks required section {section}: {THREE_AXIS_ASSET}"
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
        for token in THREE_AXIS_OUTPUT_TOKENS:
            if token not in contract_text:
                errors.append(f"output contract lacks three-axis requirement: {token}")
        for asset_name in sorted(set(ASSET_RE.findall(contract_text))):
            if not (root / "assets" / asset_name).exists():
                errors.append(f"asset named by output contract is missing: assets/{asset_name}")

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

    for filename in THREE_AXIS_EXECUTION_ASSETS:
        path = root / "assets" / filename
        if not path.exists():
            errors.append(f"execution asset is missing: assets/{filename}")
            continue
        if "影响维度" not in path.read_text(encoding="utf-8"):
            errors.append(
                "execution asset lacks three-axis mapping field 影响维度: "
                f"assets/{filename}"
            )

    for filename in ("due-diligence-playbook.md", "positions-and-documents.md"):
        path = references_dir / filename
        if not path.exists():
            errors.append(f"routed workflow reference is missing: references/{filename}")
            continue
        workflow_text = path.read_text(encoding="utf-8")
        for route in TRANSACTION_ROUTES:
            if route not in workflow_text:
                errors.append(f"{filename} lacks transaction route: {route}")
        for token in LISTED_CONTROL_COVERAGE:
            if token not in workflow_text:
                errors.append(f"{filename} lacks L-CONTROL coverage: {token}")

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

    for path in [skill_path, *references_dir.glob("*.md"), *(root / "assets").glob("*.md")]:
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
