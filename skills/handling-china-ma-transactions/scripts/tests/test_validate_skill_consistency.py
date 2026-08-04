import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_skill_consistency.py"


class SkillConsistencyTests(unittest.TestCase):
    def test_every_asset_declares_common_matter_metadata(self):
        required_fields = [
            "事项：",
            "路由：",
            "立场：",
            "As-of / 法律核验日：",
            "材料范围 / 版本：",
            "关键假设：",
            "法域：",
            "完成状态：",
        ]
        for path in sorted((ROOT / "assets").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for field in required_fields:
                with self.subTest(asset=path.name, field=field):
                    self.assertIn(field, text)

    def test_skill_is_internally_consistent(self):
        spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.validate_skill(ROOT), [])

    def test_validator_rejects_asset_missing_common_field(self):
        spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            asset = copied_root / "assets" / "approval-matrix-template.md"
            asset.write_text(
                asset.read_text(encoding="utf-8").replace("关键假设：", "假设记录："),
                encoding="utf-8",
            )
            errors = module.validate_skill(copied_root)

        self.assertIn(
            "asset lacks common matter field 关键假设：: assets/approval-matrix-template.md",
            errors,
        )

    def test_validator_rejects_missing_three_axis_product_language(self):
        spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            skill = copied_root / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8").replace(
                    "三维决策内核", "交易分析框架"
                ),
                encoding="utf-8",
            )
            errors = module.validate_skill(copied_root)

        self.assertIn(
            "SKILL.md lacks three-axis product contract: 三维决策内核",
            errors,
        )

    def test_validator_rejects_missing_three_axis_asset(self):
        spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            asset = copied_root / "assets" / "three-axis-structure-template.md"
            if asset.exists():
                asset.unlink()
            errors = module.validate_skill(copied_root)

        self.assertIn(
            "required three-axis asset is missing: assets/three-axis-structure-template.md",
            errors,
        )

    def test_validator_rejects_execution_asset_without_axis_mapping(self):
        spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "skill"
            shutil.copytree(ROOT, copied_root)
            asset = copied_root / "assets" / "approval-matrix-template.md"
            asset.write_text(
                asset.read_text(encoding="utf-8").replace(
                    "影响维度", "关联事项"
                ),
                encoding="utf-8",
            )
            errors = module.validate_skill(copied_root)

        self.assertIn(
            "execution asset lacks three-axis mapping field 影响维度: assets/approval-matrix-template.md",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
