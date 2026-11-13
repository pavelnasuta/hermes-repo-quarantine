from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL = Path("skills/hermes-repo-quarantine/SKILL.md")
REQUIRED_FILES = (
    DEFAULT_SKILL,
    Path("skills/hermes-repo-quarantine/references/trust-model.md"),
    Path("skills/hermes-repo-quarantine/references/evaluation.md"),
    Path("README.md"),
    Path("LICENSE"),
    Path("SECURITY.md"),
    Path("AGENTS.md"),
    Path("specs/quarantine-contract.md"),
    Path("specs/quarantine-attestation-schema.json"),
    Path("scripts/quarantine_preflight.py"),
    Path("examples/quarantine-attestation.example.json"),
    Path("agents/hermes/SKILL.md"),
    Path("agents/claude-code/SKILL.md"),
    Path("agents/codex/AGENTS.md"),
    Path("skills/hermes-repo-quarantine/scripts/quarantine_preflight.py"),
    Path("skills/hermes-repo-quarantine/references/quarantine-attestation-schema.json"),
    Path("skills/hermes-repo-quarantine/references/quarantine-attestation.example.json"),
)
FORBIDDEN_PATTERNS = (
    "/" + "root/",
    "~/" + ".hermes",
    r"gho_[A-Za-z0-9_]+",
    r"sk-[A-Za-z0-9_-]+",
    "hermes-" + "untrusted-repo-sandbox",
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the public skill package.")
    parser.add_argument("--skill", type=Path, default=DEFAULT_SKILL)
    args = parser.parse_args()
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            fail(errors, f"Missing required file: {relative_path}")

    skill_path = ROOT / args.skill
    if not skill_path.is_file():
        fail(errors, f"Missing skill file: {args.skill}")
    else:
        skill = skill_path.read_text(encoding="utf-8")
        if not skill.startswith("---\n") or "\n---\n" not in skill:
            fail(errors, "SKILL.md must begin with YAML frontmatter")
        for required in ("name: hermes-repo-quarantine", "version:", "license: MIT"):
            if required not in skill:
                fail(errors, f"SKILL.md missing required metadata: {required}")

    readme_path = ROOT / "README.md"
    if readme_path.is_file():
        readme = readme_path.read_text(encoding="utf-8")
        for required in (
            "hermes skills tap add pavelnasuta/hermes-repo-quarantine",
            "hermes skills install pavelnasuta/hermes-repo-quarantine/skills/hermes-repo-quarantine",
        ):
            if required not in readme:
                fail(errors, f"README.md missing install command: {required}")

    adapter_paths = (
        Path("agents/hermes/SKILL.md"),
        Path("agents/claude-code/SKILL.md"),
        Path("agents/codex/AGENTS.md"),
    )
    shared_command = "python scripts/quarantine_preflight.py --format json"
    for adapter_path in adapter_paths:
        full_path = ROOT / adapter_path
        if full_path.is_file() and full_path.read_text(encoding="utf-8").count(shared_command) != 1:
            fail(errors, f"Adapter must contain exactly one shared preflight command: {adapter_path}")
        if full_path.is_file() and "AGENTS.md" not in full_path.read_text(encoding="utf-8"):
            fail(errors, f"Adapter must reference the canonical contract: {adapter_path}")

    ignored_patterns = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for relative_path in REQUIRED_FILES:
        if str(relative_path) in ignored_patterns or relative_path.name in ignored_patterns:
            fail(errors, f"Required file is ignored by .gitignore: {relative_path}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text):
                fail(errors, f"Forbidden private or retired identifier in {path.relative_to(ROOT)}: {pattern}")

    if errors:
        print("Validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
