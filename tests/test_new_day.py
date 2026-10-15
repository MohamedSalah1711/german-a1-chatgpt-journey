"""Regression tests for non-destructive, page-aware German A1 day generation."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generator", ROOT / "scripts/new_day.py")
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


class NewDayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ("scripts", "templates", "data", "days"):
            (self.root / folder).mkdir()
        for rel in (
            "scripts/new_day.py", "templates/day-template.md",
            "data/verbs_a1.json", "data/grammar_plan.json",
            "data/course_verbs.json", "progress.json", "CURRENT_STATE.md",
        ):
            shutil.copy2(ROOT / rel, self.root / rel)

    def run_generator(self, *args):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts/new_day.py"), *args],
            capture_output=True, text=True, encoding="utf-8", cwd=self.root,
        )

    def finish_previous_day(self):
        path = self.root / "progress.json"
        progress = json.loads(path.read_text(encoding="utf-8"))
        progress["generated_days"][0]["completed"] = True
        path.write_text(json.dumps(progress, ensure_ascii=False), encoding="utf-8")
        return progress

    def test_incomplete_day_never_changed(self):
        old_progress = (self.root / "progress.json").read_bytes()
        old_state = (self.root / "CURRENT_STATE.md").read_bytes()
        result = self.run_generator("--date", "2026-10-15")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("incomplete day", result.stderr)
        self.assertEqual(old_progress, (self.root / "progress.json").read_bytes())
        self.assertEqual(old_state, (self.root / "CURRENT_STATE.md").read_bytes())

    def test_new_worksheet_does_not_claim_study_or_touch_state(self):
        old = self.finish_previous_day()
        state = (self.root / "CURRENT_STATE.md").read_bytes()
        result = self.run_generator("--date", "2026-10-15")
        self.assertEqual(result.returncode, 0, result.stderr)
        worksheet = (self.root / "days/2026-10-15-day-002.md").read_text(encoding="utf-8")
        self.assertIn("General A1 practice only", worksheet)
        self.assertIn("Printed page 81 / PDF viewer page 82", worksheet)
        self.assertNotIn("{{", worksheet)
        updated = json.loads((self.root / "progress.json").read_text(encoding="utf-8"))
        self.assertEqual(old["course_progress"], updated["course_progress"])
        self.assertEqual(old["skills"], updated["skills"])
        self.assertEqual(state, (self.root / "CURRENT_STATE.md").read_bytes())
        self.assertFalse(updated["generated_days"][-1]["completed"])
        self.assertIsNone(updated["generated_days"][-1]["score"])

    def test_dry_run_and_existing_file_are_safe(self):
        self.finish_previous_day()
        previous = (self.root / "progress.json").read_bytes()
        dry = self.run_generator("--date", "2026-10-15", "--dry-run")
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertEqual(previous, (self.root / "progress.json").read_bytes())
        target = self.root / "days/2026-10-15-day-002.md"
        target.write_text("KEEP", encoding="utf-8")
        blocked = self.run_generator("--date", "2026-10-15")
        self.assertNotEqual(blocked.returncode, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "KEEP")

    def test_mapped_verbs_and_no_repeat_after_practice(self):
        general = json.loads((ROOT / "data/verbs_a1.json").read_text(encoding="utf-8"))
        mapped = json.loads((ROOT / "data/course_verbs.json").read_text(encoding="utf-8"))
        progress = {"course_progress": {"next_printed_page": 81}, "lesson_sessions": []}
        selected, source = GEN.select_verbs(general, mapped, progress, 2, 10)
        self.assertEqual(selected[0]["verb"], "anprobieren")
        self.assertEqual(len(selected), 10)
        self.assertIn("Book page 81", source)
        progress["lesson_sessions"] = [{"verbs": [v["verb"] for v in selected]}]
        next_selected, source = GEN.select_verbs(general, mapped, progress, 2, 10)
        self.assertEqual(len({v["verb"] for v in next_selected}), 10)
        self.assertIn("General A1 practice only", source)


if __name__ == "__main__":
    unittest.main()
