from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
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

    def test_multi_agent_contract_and_adapters_exist(self) -> None:
        required = (
            "AGENTS.md",
            "specs/quarantine-contract.md",
            "scripts/quarantine_preflight.py",
            "examples/quarantine-attestation.example.json",
            "agents/hermes/SKILL.md",
            "agents/claude-code/SKILL.md",
            "agents/codex/AGENTS.md",
            "skills/hermes-repo-quarantine/scripts/quarantine_preflight.py",
            "skills/hermes-repo-quarantine/references/quarantine-attestation-schema.json",
            "skills/hermes-repo-quarantine/references/quarantine-attestation.example.json",
        )
        for relative_path in required:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

        shared_command = "python scripts/quarantine_preflight.py --format json"
        for relative_path in (
            "agents/hermes/SKILL.md",
            "agents/claude-code/SKILL.md",
            "agents/codex/AGENTS.md",
        ):
            self.assertIn(shared_command, (ROOT / relative_path).read_text(encoding="utf-8"))

        portable_skill = (ROOT / "skills/hermes-repo-quarantine/SKILL.md").read_text(encoding="utf-8")
        self.assertIn(shared_command, portable_skill)
        self.assertIn("references/quarantine-attestation-schema.json", portable_skill)

        portable_root = ROOT / "skills/hermes-repo-quarantine"
        portable_preflight = subprocess.run(
            [
                sys.executable,
                "scripts/quarantine_preflight.py",
                "--format",
                "json",
                "--attestation",
                "references/quarantine-attestation.example.json",
            ],
            cwd=portable_root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(portable_preflight.returncode, 0, portable_preflight.stdout + portable_preflight.stderr)
        self.assertEqual(json.loads(portable_preflight.stdout)["decision"], "ALLOW_READ_ONLY")

    def test_preflight_accepts_example_and_blocks_missing_attestation(self) -> None:
        allowed = subprocess.run(
            [
                sys.executable,
                "scripts/quarantine_preflight.py",
                "--format",
                "json",
                "--attestation",
                "examples/quarantine-attestation.example.json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)
        self.assertEqual(allowed.stderr, "")
        self.assertEqual(json.loads(allowed.stdout)["decision"], "ALLOW_READ_ONLY")

        blocked = subprocess.run(
            [sys.executable, "scripts/quarantine_preflight.py", "--format", "json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(blocked.returncode, 2, blocked.stdout + blocked.stderr)
        self.assertIn('"decision": "BLOCKED"', blocked.stdout)

    def test_preflight_schema_is_complete_and_each_control_is_enforced(self) -> None:
        schema_path = ROOT / "specs/quarantine-attestation-schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        required_controls = schema["required_controls"]
        example = json.loads(
            (ROOT / "examples/quarantine-attestation.example.json").read_text(encoding="utf-8")
        )
        self.assertEqual(set(required_controls), {key for key, value in example.items() if value is True})

        for control in required_controls:
            for mode in ("false", "missing"):
                with self.subTest(control=control, mode=mode), tempfile.TemporaryDirectory() as directory:
                    attestation_path = Path(directory) / "attestation.json"
                    invalid = dict(example)
                    if mode == "false":
                        invalid[control] = False
                    else:
                        invalid.pop(control)
                    attestation_path.write_text(json.dumps(invalid), encoding="utf-8")
                    result = subprocess.run(
                        [
                            sys.executable,
                            "scripts/quarantine_preflight.py",
                            "--format",
                            "json",
                            "--attestation",
                            str(attestation_path),
                        ],
                        cwd=ROOT,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload["decision"], "BLOCKED")
                    self.assertIn(control, payload["missing_controls"])

    def test_preflight_json_errors_and_adapters_are_strict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            malformed = Path(directory) / "malformed.json"
            malformed.write_text("{not-json", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/quarantine_preflight.py",
                    "--format",
                    "json",
                    "--attestation",
                    str(malformed),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["decision"], "BLOCKED")

            non_object = Path(directory) / "non-object.json"
            non_object.write_text("[]", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/quarantine_preflight.py",
                    "--format",
                    "json",
                    "--attestation",
                    str(non_object),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["decision"], "BLOCKED")

        shared_command = "python scripts/quarantine_preflight.py --format json"
        for relative_path in (
            "agents/hermes/SKILL.md",
            "agents/claude-code/SKILL.md",
            "agents/codex/AGENTS.md",
        ):
            content = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertEqual(content.count(shared_command), 1, relative_path)
            self.assertIn("AGENTS.md", content, relative_path)

        validator = (ROOT / "scripts/validate.py").read_text(encoding="utf-8")
        self.assertIn(".count(shared_command) != 1", validator)


if __name__ == "__main__":
    unittest.main()
