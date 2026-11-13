from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "specs/quarantine-attestation-schema.json"


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def load_required_controls() -> tuple[str, ...]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    controls = schema.get("required_controls")
    if not isinstance(controls, list) or not controls or any(
        not isinstance(control, str) or not control for control in controls
    ):
        raise ValueError("schema has no valid required_controls list")
    if len(controls) != len(set(controls)):
        raise ValueError("schema contains duplicate required controls")
    return tuple(controls)


def blocked(attestation: Path, required_controls: tuple[str, ...], reason: str) -> int:
    emit(
        {
            "attestation": str(attestation),
            "decision": "BLOCKED",
            "missing_controls": list(required_controls),
            "reason": reason,
        }
    )
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a RepoQuarantine sandbox attestation.")
    parser.add_argument("--attestation", type=Path, default=Path(".repoquarantine.json"))
    parser.add_argument("--format", choices=("json",), default="json")
    args = parser.parse_args()

    try:
        required_controls = load_required_controls()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        emit(
            {
                "attestation": str(args.attestation),
                "decision": "BLOCKED",
                "missing_controls": [],
                "reason": f"invalid bundled schema: {error}",
            }
        )
        return 2

    if not args.attestation.is_file():
        return blocked(args.attestation, required_controls, "attestation file is missing")

    try:
        attestation = json.loads(args.attestation.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return blocked(args.attestation, required_controls, f"invalid attestation: {error}")

    if not isinstance(attestation, dict):
        return blocked(args.attestation, required_controls, "attestation must be a JSON object")

    missing = [control for control in required_controls if attestation.get(control) is not True]
    decision = "ALLOW_READ_ONLY" if not missing else "BLOCKED"
    emit(
        {
            "attestation": str(args.attestation),
            "decision": decision,
            "missing_controls": missing,
            "note": "This attestation gate does not create or prove OS-level isolation.",
        }
    )
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
