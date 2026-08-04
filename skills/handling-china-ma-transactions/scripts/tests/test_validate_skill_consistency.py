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


if __name__ == "__main__":
    unittest.main()
