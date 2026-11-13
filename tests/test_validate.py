from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ValidateRepositoryTests(unittest.TestCase):
    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/validate.py", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_repository_contract_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Validation passed", result.stdout)

    def test_missing_skill_is_reported(self) -> None:
        result = self.run_validator("--skill", "skills/missing/SKILL.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing", (result.stdout + result.stderr).lower())


if __name__ == "__main__":
    unittest.main()
