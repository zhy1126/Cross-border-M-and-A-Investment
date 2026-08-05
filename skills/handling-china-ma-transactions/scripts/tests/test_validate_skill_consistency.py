import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_skill_consistency.py"

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
DELIVERY_VIEW_TOKENS = (
    "管理层决策版",
    "律师执行版",
    "同一底层分析",
)
DELIVERY_CONSISTENCY_RULE = (
    "两个版本的方案编号、关键事实、状态、推荐结论和时间线必须一致"
)
DELIVERY_SHARED_FIELDS = (
    "方案 ID",
    "关键事实",
    "状态",
    "推荐结论",
    "时间线",
)
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
CURRENT_README_LEGACY_CAPABILITIES = (
    "- **法律尽职调查**：红旗尽调、完整尽调、Major Issues、更新尽调及问题—条款映射；",
    "- **交易文件与谈判**：SPA/APA、股份转让或认购协议、披露、保证、赔偿、责任限制和交割机制；",
    "- **审批与交割**：经营者集中、国资、外资准入、安全审查、ODI/外汇、数据、技术出口和出口管制；",
)
CURRENT_SKILL_LEGACY_CAPABILITIES = (
    "description: Use when advising on China-focused investment or M&A transactions, including legal due diligence, transaction structuring, listed-company control acquisitions, private share or asset purchases, SPA/APA terms, regulatory approvals, signing or closing, negotiation, and buyer- or seller-side issue analysis.",
    "- Use the three-axis kernel before working the lifecycle: structure → contact/NDA → diligence → documents/negotiation → signing → effectiveness/approvals → closing → post-closing/integration → claims.",
)
CURRENT_UI_LEGACY_CAPABILITIES = (
    'short_description: "以三维决策内核驱动中国并购结构与执行"',
    'default_prompt: "Use $handling-china-ma-transactions from the buyer perspective. For structure requests, analyze 控制权、收购方式、合并财务报表 in that causal order as the 三维 decision kernel, then map diligence, approvals, terms, negotiation and closing actions to the affected axes. For non-structure requests, identify only the affected axes and do not fabricate a full transaction structure."',
)
CURRENT_SURFACE_LEGACY_CAPABILITIES = {
    "README.md": CURRENT_README_LEGACY_CAPABILITIES,
    "SKILL.md": CURRENT_SKILL_LEGACY_CAPABILITIES,
    "agents/openai.yaml": CURRENT_UI_LEGACY_CAPABILITIES,
}
POSITIVE_OVERCLAIM_VARIANTS = (
    CURRENT_README_LEGACY_CAPABILITIES
    + CURRENT_SKILL_LEGACY_CAPABILITIES
    + CURRENT_UI_LEGACY_CAPABILITIES
    + (
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
ALLOWED_BOUNDARY_VARIANTS = (
    "本 Skill 只负责交易结构方案规划",
    "本 Skill 不负责法律尽职调查或完整尽调",
    "交易文件审阅、SPA 审阅和全议题谈判转交后续专业能力",
    "本 Skill 仅输出尽调任务包和交易文件任务包",
    "本 Skill 不会执行审批申报、申报或交割管理",
    "会计结论由管理层和会计师出具",
    "整合与索赔仅作为后续任务包接口",
)
OVERCLAIM_SURFACES = (
    "SKILL.md",
    "README.md",
    "agents/openai.yaml",
)
COMMON_ASSET_METADATA = (
    "事项：",
    "路由：L-CONTROL / P-EQUITY / P-ASSET",
    "立场：Buyer / Seller",
    "As-of / 法律核验日：",
    "材料范围 / 版本：",
    "关键假设：",
    "法域：中华人民共和国境内",
    "完成状态：passed / passed_with_limitations / blocked",
)


def load_validator():
    spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_heading(text: str, title: str):
    return re.search(
        rf"^#{{1,6}}\s+(?:\d+(?:\.\d+)*[.、]?\s+)?{re.escape(title)}\s*$",
        text,
        re.MULTILINE,
    )


def find_numbered_heading(text: str, index: int, title: str):
    return re.search(
        rf"^#{{1,6}}\s+{index}[.、]\s+{re.escape(title)}\s*$",
        text,
        re.MULTILINE,
    )


def find_numbered_entry(text: str, index: int, title: str):
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


def extract_heading_section(text: str, title: str) -> str:
    heading = find_heading(text, title)
    if heading is None:
        return ""
    level = len(heading.group(0)) - len(heading.group(0).lstrip("#"))
    next_heading = re.search(
        rf"^#{{1,{level}}}\s+",
        text[heading.end() :],
        re.MULTILINE,
    )
    end = heading.end() + next_heading.start() if next_heading else len(text)
    return text[heading.end() : end]


def table_rows(text: str):
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = tuple(cell.strip().strip("`") for cell in stripped[1:-1].split("|"))
        if cells and not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            rows.append(cells)
    return rows


def render_intake_fixture(omit_group=None) -> str:
    lines = ["# 事项入项表", "", *COMMON_ASSET_METADATA, "", "## 三维目标"]
    for index, group in enumerate(FIXED_INPUT_GROUPS, start=1):
        if group != omit_group:
            lines.extend(
                (
                    "",
                    f"## {index}. {group}",
                    "| 字段 | 要求等级 | 事实状态 | 对方案的影响 | 责任人 | 关闭证据 |",
                    "|---|---|---|---|---|---|",
                    "| 项目阶段 | start-required | confirmed | 无 | 项目负责人 | 来源页码 |",
                )
            )
    lines.extend(
        (
            "",
            "要求等级与事实状态分开记录。",
            "`start-required` 缺失时不能启动结构化方案规划。",
            "`assumption-allowed` 缺失时可基于明确假设继续。",
            "`recommendation-blocker` 可以比较路径，但缺失时不得给出确定推荐，整体状态为 `blocked`。",
            "事实状态只使用 `confirmed`、`assumed`、`missing`、`conflicting`、`external-confirmation-pending`。",
            "每一非 `confirmed` 项必须写明对方案的影响、责任人和关闭证据。",
            "",
        )
    )
    text = "\n".join(lines)
    if omit_group is not None:
        assert omit_group not in text
    return text


def render_output_fixture(demote_section=None) -> str:
    lines = ["# 三维结构方案", "", *COMMON_ASSET_METADATA]
    for index, section in enumerate(FIXED_OUTPUT_SECTIONS, start=1):
        if section == demote_section:
            lines.extend(("", f"正文提及：{section}"))
        else:
            lines.extend(("", f"## {index}. {section}"))
    lines.extend(
        (
            "",
            "三维执行摘要",
            "控制权矩阵",
            "收购方式比较矩阵",
            "并表支持与证据矩阵",
            "跨维度依赖",
            "P-ASSET 分支：资产边界与经营主导权",
            "P-ASSET 分支：资产收购或业务合并",
            "投入与实质性加工处理过程",
            "集中度测试",
            "确认日 / 购买日",
            "",
        )
    )
    text = "\n".join(lines)
    if demote_section is not None:
        assert demote_section in text
        assert find_heading(text, demote_section) is None
    return text


def render_task_packages_fixture(omit_field=None, omit_package=None) -> str:
    lines = ["# 后续任务包", "", *COMMON_ASSET_METADATA]
    for index, package in enumerate(DOWNSTREAM_TASK_PACKAGES, start=1):
        if package == omit_package:
            continue
        fields = list(DOWNSTREAM_TASK_PACKAGE_FIELDS)
        if omit_field is not None and package == omit_field[0]:
            fields.remove(omit_field[1])
        lines.extend(
            (
                "",
                f"## {index}. {package}",
                "| " + " | ".join(fields) + " |",
                "|" + "|".join("---" for _ in fields) + "|",
                "",
            )
        )
    return "\n".join(lines)


def without_snippets(text: str, snippets) -> str:
    for snippet in snippets:
        text = text.replace(snippet, "")
    return text


def add_surface_probe(text: str, surface: str, snippets) -> str:
    if surface == "agents/openai.yaml":
        return text + "\n  overclaim_probe: |\n" + "\n".join(
            f"    {snippet}" for snippet in snippets
        ) + "\n"
    return text + "\n" + "\n".join(snippets) + "\n"


def replace_all(text: str, token: str, replacement: str) -> str:
    assert token in text
    mutated = text.replace(token, replacement)
    assert token not in mutated
    return mutated


class SkillConsistencyTests(unittest.TestCase):
    def assertContainsTokens(self, path: Path, tokens):
        self.assertTrue(path.exists(), f"required contract file is missing: {path}")
        text = path.read_text(encoding="utf-8")
        missing = [token for token in tokens if token not in text]
        self.assertEqual([], missing, f"{path.name} lacks required contract tokens")

    def assertMutationDelta(self, before, after, expected):
        self.assertEqual(set(expected), set(after).difference(before))

    def assertOrderedOutputSections(self, path: Path, require_headings: bool):
        self.assertTrue(path.exists(), f"required contract file is missing: {path}")
        text = path.read_text(encoding="utf-8")
        positions = []
        for index, title in enumerate(FIXED_OUTPUT_SECTIONS, start=1):
            if require_headings:
                match = find_heading(text, title)
            else:
                match = re.search(
                    rf"^(?:#{{1,6}}\s+)?{index}[.、]\s+(?:\*\*)?"
                    rf"{re.escape(title)}(?:\*\*)?(?:[：:；;。].*)?$",
                    text,
                    re.MULTILINE,
                )
            self.assertIsNotNone(
                match, f"{path.name} lacks ordered section {index}: {title}"
            )
            positions.append(match.start())
        self.assertEqual(positions, sorted(positions), f"{path.name} section order changed")

    def test_three_axis_reference_preserves_causal_sequence(self):
        text = (ROOT / "references" / "three-axis-transaction-engine.md").read_text(
            encoding="utf-8"
        )
        tokens = (
            "先确定控制权目标",
            "围绕控制目标生成和比较路径",
            "从前两维提取",
        )
        positions = [text.index(token) for token in tokens]
        self.assertEqual(positions, sorted(positions))

    def test_validator_rejects_broken_three_axis_causality(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            before = module.validate_skill(copied_root)
            reference = (
                copied_root / "references" / "three-axis-transaction-engine.md"
            )
            reference.write_text(
                replace_all(
                    reference.read_text(encoding="utf-8"),
                    "围绕控制目标生成和比较路径",
                    "独立于控制目标罗列交易路径",
                ),
                encoding="utf-8",
            )
            after = module.validate_skill(copied_root)

        self.assertMutationDelta(
            before,
            after,
            {
                "three-axis reference breaks causal sequence: 围绕控制目标生成和比较路径"
            },
        )

    def test_p_asset_has_route_adapted_structure_and_accounting_contract(self):
        structure = (ROOT / "assets" / "three-axis-structure-template.md").read_text(
            encoding="utf-8"
        )
        accounting = (
            ROOT / "references" / "accounting-control-and-consolidation.md"
        ).read_text(encoding="utf-8")
        for token in (
            "P-ASSET 分支：资产边界与经营主导权",
            "P-ASSET 分支：资产收购或业务合并",
            "投入与实质性加工处理过程",
            "集中度测试",
            "确认日 / 购买日",
        ):
            with self.subTest(token=token):
                self.assertIn(token, structure)
                self.assertIn(token, accounting)

    def test_private_route_references_preserve_three_paths_and_exclusion_reason(self):
        three_path_pattern = r"(?:三个方案|三条路径|基准[^\n]*备选[^\n]*兜底)"
        exclusion_pattern = r"(?:排除原因|被排除路径[^\n]{0,12}原因)"
        for filename in ("private-equity-ma.md", "private-asset-ma.md"):
            text = (ROOT / "references" / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertRegex(text, three_path_pattern)
                self.assertRegex(text, exclusion_pattern)

    def test_intake_template_uses_six_numbered_table_sections_in_order(self):
        path = ROOT / "assets" / "matter-intake-template.md"
        self.assertTrue(path.exists(), f"required contract file is missing: {path}")
        text = path.read_text(encoding="utf-8")
        positions = []
        for index, group in enumerate(FIXED_INPUT_GROUPS, start=1):
            with self.subTest(group=group):
                heading = find_numbered_heading(text, index, group)
                self.assertIsNotNone(heading, f"missing numbered input group: {group}")
                positions.append(heading.start())
                self.assertTrue(
                    table_rows(extract_heading_section(text, group)),
                    f"input group lacks a field table: {group}",
                )
        self.assertEqual(positions, sorted(positions))

    def test_intake_reference_uses_the_same_six_numbered_entries_in_order(self):
        path = ROOT / "references" / "intake-routing-and-gates.md"
        text = path.read_text(encoding="utf-8")
        positions = []
        for index, group in enumerate(FIXED_INPUT_GROUPS, start=1):
            with self.subTest(group=group):
                entry = find_numbered_entry(text, index, group)
                self.assertIsNotNone(entry, f"missing structured input entry: {group}")
                positions.append(entry.start())
        self.assertEqual(positions, sorted(positions))

    def test_intake_contract_separates_requirement_levels_and_fact_statuses(self):
        intake = ROOT / "assets" / "matter-intake-template.md"
        self.assertContainsTokens(intake, FIELD_REQUIREMENT_LEVELS + FACT_STATUSES)
        headers = table_rows(intake.read_text(encoding="utf-8"))
        matching_headers = [
            row for row in headers if all(field in row for field in INPUT_TRACKING_FIELDS)
        ]
        self.assertTrue(
            matching_headers,
            "matter intake must keep requirement level, fact status and closure fields in separate columns",
        )

        reference = (
            ROOT / "references" / "intake-routing-and-gates.md"
        ).read_text(encoding="utf-8")
        self.assertIn("要求等级与事实状态分开记录", reference)
        for token in FIELD_REQUIREMENT_LEVELS + FACT_STATUSES:
            with self.subTest(token=token):
                self.assertIn(token, reference)

    def test_intake_contract_enforces_start_and_recommendation_gates(self):
        reference = (
            ROOT / "references" / "intake-routing-and-gates.md"
        ).read_text(encoding="utf-8")
        self.assertRegex(
            reference, r"`start-required`[^。\n]*缺失时[^。\n]*不能启动"
        )
        self.assertRegex(
            reference,
            r"`recommendation-blocker`[^。\n]*可以比较路径[^。\n]*缺失时"
            r"[^。\n]*不得给出确定推荐[^。\n]*`blocked`",
        )

    def test_non_confirmed_input_requires_impact_owner_and_closing_evidence(self):
        reference = (
            ROOT / "references" / "intake-routing-and-gates.md"
        ).read_text(encoding="utf-8")
        self.assertRegex(
            reference,
            r"每一非\s*`confirmed`\s*项[^。\n]*对方案的影响[^。\n]*责任人[^。\n]*关闭证据",
        )
        intake_headers = table_rows(
            (ROOT / "assets" / "matter-intake-template.md").read_text(encoding="utf-8")
        )
        self.assertTrue(
            any(
                all(field in row for field in ("对方案的影响", "责任人", "关闭证据"))
                for row in intake_headers
            ),
            "matter intake lacks non-confirmed-item closure columns",
        )

    def test_output_template_uses_eight_fixed_headings_in_order(self):
        self.assertOrderedOutputSections(
            ROOT / "assets" / "three-axis-structure-template.md",
            require_headings=True,
        )

    def test_output_contract_uses_eight_fixed_ordered_sections(self):
        self.assertOrderedOutputSections(
            ROOT / "references" / "output-contract.md",
            require_headings=False,
        )

    def test_delivery_views_share_identifiers_facts_status_conclusion_and_timeline(self):
        path = ROOT / "references" / "output-contract.md"
        self.assertContainsTokens(path, DELIVERY_VIEW_TOKENS)
        text = path.read_text(encoding="utf-8")
        self.assertIn(DELIVERY_CONSISTENCY_RULE, text)

    def test_output_template_contains_both_views_with_the_same_shared_fields(self):
        path = ROOT / "assets" / "three-axis-structure-template.md"
        text = path.read_text(encoding="utf-8")
        for view in ("管理层决策版", "律师执行版"):
            with self.subTest(view=view):
                section = extract_heading_section(text, view)
                self.assertTrue(section, f"missing delivery view section: {view}")
                self.assertTrue(
                    any(
                        all(field in row for field in DELIVERY_SHARED_FIELDS)
                        for row in table_rows(section)
                    ),
                    f"{view} lacks the shared identity and conclusion fields",
                )

    def test_each_downstream_task_package_uses_the_complete_common_schema(self):
        path = ROOT / "assets" / "downstream-task-packages-template.md"
        self.assertTrue(path.exists(), f"required contract file is missing: {path}")
        text = path.read_text(encoding="utf-8")
        for package in DOWNSTREAM_TASK_PACKAGES:
            with self.subTest(package=package):
                section = extract_heading_section(text, package)
                self.assertTrue(section, f"missing package section: {package}")
                self.assertIn(
                    DOWNSTREAM_TASK_PACKAGE_FIELDS,
                    table_rows(section),
                    f"{package} does not use the complete common schema",
                )

    def test_product_surfaces_position_the_skill_as_structure_planning(self):
        for path in (
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT.parents[1] / "README.md",
        ):
            with self.subTest(path=path.name):
                self.assertContainsTokens(path, ("交易结构方案规划",))

    def test_current_legacy_surface_capabilities_are_rejected_until_removed(self):
        errors = set(load_validator().validate_skill(ROOT))
        surface_paths = {
            "README.md": ROOT.parents[1] / "README.md",
            "SKILL.md": ROOT / "SKILL.md",
            "agents/openai.yaml": ROOT / "agents" / "openai.yaml",
        }
        for surface, legacy_lines in CURRENT_SURFACE_LEGACY_CAPABILITIES.items():
            text = surface_paths[surface].read_text(encoding="utf-8")
            present = [line for line in legacy_lines if line in text]
            if not present:
                continue
            with self.subTest(surface=surface):
                expected = {
                    f"downstream overclaim in {surface}: {line}" for line in present
                }
                self.assertEqual(set(), expected.difference(errors))

    def test_skill_is_internally_consistent(self):
        module = load_validator()
        self.assertEqual(module.validate_skill(ROOT), [])

    def test_validator_reports_exact_error_when_an_input_group_is_removed(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            intake = copied_root / "assets" / "matter-intake-template.md"
            intake.write_text(render_intake_fixture(), encoding="utf-8")
            before = module.validate_skill(copied_root)
            intake.write_text(
                render_intake_fixture(omit_group="事项信息"), encoding="utf-8"
            )
            after = module.validate_skill(copied_root)

        self.assertMutationDelta(
            before,
            after,
            {"matter intake lacks fixed input group: 事项信息"},
        )

    def test_validator_reports_exact_error_when_an_output_section_is_removed(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            output = copied_root / "assets" / "three-axis-structure-template.md"
            output.write_text(render_output_fixture(), encoding="utf-8")
            before = module.validate_skill(copied_root)
            output.write_text(
                render_output_fixture(demote_section="项目状态及分析边界"),
                encoding="utf-8",
            )
            after = module.validate_skill(copied_root)

        self.assertMutationDelta(
            before,
            after,
            {"three-axis asset lacks fixed output section: 项目状态及分析边界"},
        )

    def test_validator_reports_exact_error_when_one_package_schema_field_is_removed(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            packages = (
                copied_root / "assets" / "downstream-task-packages-template.md"
            )
            fixture = render_task_packages_fixture(
                omit_field=("尽调任务包", "完成证据")
            )
            self.assertNotIn(
                "完成证据", extract_heading_section(fixture, "尽调任务包")
            )
            for package in DOWNSTREAM_TASK_PACKAGES[1:]:
                self.assertIn(
                    DOWNSTREAM_TASK_PACKAGE_FIELDS,
                    table_rows(extract_heading_section(fixture, package)),
                )
            skill = copied_root / "SKILL.md"
            if "assets/downstream-task-packages-template.md" not in skill.read_text(
                encoding="utf-8"
            ):
                skill.write_text(
                    skill.read_text(encoding="utf-8")
                    + "\n[task packages](assets/downstream-task-packages-template.md)\n",
                    encoding="utf-8",
                )
            packages.write_text(render_task_packages_fixture(), encoding="utf-8")
            before = module.validate_skill(copied_root)
            packages.write_text(fixture, encoding="utf-8")
            after = module.validate_skill(copied_root)

        self.assertMutationDelta(
            before,
            after,
            {"downstream task package 尽调任务包 lacks required field: 完成证据"},
        )

    def test_validator_reports_exact_error_when_a_package_section_is_removed(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            packages = (
                copied_root / "assets" / "downstream-task-packages-template.md"
            )
            skill = copied_root / "SKILL.md"
            if "assets/downstream-task-packages-template.md" not in skill.read_text(
                encoding="utf-8"
            ):
                skill.write_text(
                    skill.read_text(encoding="utf-8")
                    + "\n[task packages](assets/downstream-task-packages-template.md)\n",
                    encoding="utf-8",
                )
            packages.write_text(render_task_packages_fixture(), encoding="utf-8")
            before = module.validate_skill(copied_root)
            fixture = render_task_packages_fixture(omit_package="尽调任务包")
            self.assertEqual("", extract_heading_section(fixture, "尽调任务包"))
            for package in DOWNSTREAM_TASK_PACKAGES[1:]:
                self.assertIn(
                    DOWNSTREAM_TASK_PACKAGE_FIELDS,
                    table_rows(extract_heading_section(fixture, package)),
                )
            packages.write_text(fixture, encoding="utf-8")
            after = module.validate_skill(copied_root)

        self.assertMutationDelta(
            before,
            after,
            {"downstream task packages template lacks package section: 尽调任务包"},
        )

    def test_validator_rejects_legacy_and_synonym_overclaims_on_every_product_surface(self):
        module = load_validator()

        for surface in OVERCLAIM_SURFACES:
            with self.subTest(surface=surface), tempfile.TemporaryDirectory() as temp_dir:
                copied_repo = Path(temp_dir) / "repo"
                shutil.copytree(ROOT.parents[1], copied_repo)
                copied_root = (
                    copied_repo / "skills" / "handling-china-ma-transactions"
                )
                path = (
                    copied_repo / "README.md"
                    if surface == "README.md"
                    else copied_root / surface
                )
                baseline_text = without_snippets(
                    path.read_text(encoding="utf-8"), POSITIVE_OVERCLAIM_VARIANTS
                )
                path.write_text(baseline_text, encoding="utf-8")
                before = module.validate_skill(copied_root)
                path.write_text(
                    add_surface_probe(
                        baseline_text, surface, POSITIVE_OVERCLAIM_VARIANTS
                    ),
                    encoding="utf-8",
                )
                after = module.validate_skill(copied_root)
                expected = {
                    f"downstream overclaim in {surface}: {claim}"
                    for claim in POSITIVE_OVERCLAIM_VARIANTS
                }
                self.assertMutationDelta(before, after, expected)

    def test_validator_allows_planning_handoff_and_task_package_boundaries(self):
        module = load_validator()

        for surface in OVERCLAIM_SURFACES:
            with self.subTest(surface=surface), tempfile.TemporaryDirectory() as temp_dir:
                copied_repo = Path(temp_dir) / "repo"
                shutil.copytree(ROOT.parents[1], copied_repo)
                copied_root = (
                    copied_repo / "skills" / "handling-china-ma-transactions"
                )
                path = (
                    copied_repo / "README.md"
                    if surface == "README.md"
                    else copied_root / surface
                )
                baseline_text = without_snippets(
                    path.read_text(encoding="utf-8"), ALLOWED_BOUNDARY_VARIANTS
                )
                path.write_text(baseline_text, encoding="utf-8")
                before = module.validate_skill(copied_root)
                path.write_text(
                    add_surface_probe(
                        baseline_text, surface, ALLOWED_BOUNDARY_VARIANTS
                    ),
                    encoding="utf-8",
                )
                after = module.validate_skill(copied_root)
                self.assertMutationDelta(before, after, set())

    def test_validator_rejects_missing_three_axis_asset(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            before = module.validate_skill(copied_root)
            asset = copied_root / "assets" / "three-axis-structure-template.md"
            if asset.exists():
                asset.unlink()
            after = module.validate_skill(copied_root)

        expected = {
            "required three-axis asset is missing: assets/three-axis-structure-template.md",
            "asset named by output contract is missing: assets/three-axis-structure-template.md",
            "broken internal link in SKILL.md: assets/three-axis-structure-template.md",
            "broken internal link in references/three-axis-transaction-engine.md: ../assets/three-axis-structure-template.md",
            *{
                f"P-ASSET accounting contract lacks route token: {token}"
                for token in (
                    "P-ASSET 分支：资产边界与经营主导权",
                    "P-ASSET 分支：资产收购或业务合并",
                    "投入与实质性加工处理过程",
                    "集中度测试",
                    "确认日 / 购买日",
                )
            },
        }
        self.assertMutationDelta(
            before,
            after,
            expected,
        )

    def test_validator_rejects_intake_without_three_axis_targets(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            before = module.validate_skill(copied_root)
            asset = copied_root / "assets" / "matter-intake-template.md"
            asset.write_text(
                replace_all(asset.read_text(encoding="utf-8"), "三维目标", "交易目标"),
                encoding="utf-8",
            )
            after = module.validate_skill(copied_root)

        self.assertMutationDelta(
            before,
            after,
            {"matter intake lacks three-axis target states: 三维目标"},
        )

    def test_validator_rejects_route_reference_without_three_axis_interface(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            before = module.validate_skill(copied_root)
            reference = copied_root / "references" / "listed-control.md"
            reference.write_text(
                replace_all(
                    reference.read_text(encoding="utf-8"),
                    "三维内核接口", "结构分析接口"
                ),
                encoding="utf-8",
            )
            after = module.validate_skill(copied_root)

        self.assertMutationDelta(
            before,
            after,
            {"listed-control.md lacks three-axis route interface: 三维内核接口"},
        )

    def test_validator_rejects_accounting_reference_without_axis_inputs(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            before = module.validate_skill(copied_root)
            reference = (
                copied_root
                / "references"
                / "accounting-control-and-consolidation.md"
            )
            reference.write_text(
                replace_all(
                    reference.read_text(encoding="utf-8"),
                    "前两维输入", "交易结构输入"
                ),
                encoding="utf-8",
            )
            after = module.validate_skill(copied_root)

        self.assertMutationDelta(
            before,
            after,
            {"accounting reference lacks three-axis input contract: 前两维输入"},
        )

    def test_nonnegotiable_objective_is_a_separate_start_required_field(self):
        text = (ROOT / "assets" / "matter-intake-template.md").read_text(
            encoding="utf-8"
        )
        rows = table_rows(extract_heading_section(text, "商业目标"))
        matching = [row for row in rows if "不可牺牲目标" in row]
        self.assertEqual(len(matching), 1)
        self.assertIn("start-required", matching[0])
        self.assertNotIn("预算", matching[0])
        self.assertNotIn("期限", matching[0])

    def test_frontmatter_description_contains_triggers_not_workflow_summary(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        description = next(
            line.removeprefix("description: ")
            for line in text.splitlines()
            if line.startswith("description: ")
        )
        self.assertTrue(description.startswith("Use when "))
        for trigger in (
            "listed-company control acquisitions",
            "staged equity acquisitions",
            "asset or business acquisitions",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, description)
        for workflow in ("by defining", "comparing transaction paths", "testing consolidation", "producing decision"):
            with self.subTest(workflow=workflow):
                self.assertNotIn(workflow, description)

    def test_unannounced_listed_connection_and_mnpi_are_a_hard_gate(self):
        text = (ROOT / "references" / "intake-routing-and-gates.md").read_text(
            encoding="utf-8"
        )
        for token in (
            "未公告上市交易或其他上市公司连接点",
            "MNPI 状态",
            "未确认前不得调用外部工具、连接器或第三方",
            "L-CONTROL、P-EQUITY 或 P-ASSET",
        ):
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_management_view_is_a_standalone_decision_deliverable(self):
        text = (ROOT / "assets" / "three-axis-structure-template.md").read_text(
            encoding="utf-8"
        )
        section = extract_heading_section(text, "管理层决策版")
        for token in (
            "方案 ID",
            "关键事实",
            "状态",
            "推荐结论",
            "时间线",
            "商业差异",
            "成立条件",
            "主要反证",
            "预算影响",
            "改道触发器",
            "管理层决策事项",
        ):
            with self.subTest(token=token):
                self.assertIn(token, section)

    def test_validator_rejects_broken_internal_markdown_link(self):
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            before = module.validate_skill(copied_root)
            reference = copied_root / "references" / "three-axis-transaction-engine.md"
            reference.write_text(
                reference.read_text(encoding="utf-8")
                + "\n[broken](../assets/not-a-real-template.md)\n",
                encoding="utf-8",
            )
            after = module.validate_skill(copied_root)

        self.assertMutationDelta(
            before,
            after,
            {
                "broken internal link in references/three-axis-transaction-engine.md: ../assets/not-a-real-template.md"
            },
        )


if __name__ == "__main__":
    unittest.main()
