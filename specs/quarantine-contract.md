# Quarantine contract

## Purpose

This contract provides a common safety decision for Hermes, Claude Code, and Codex before they interact with untrusted code. It is a **workflow gate**, not an OS sandbox or malware detector.

## Authoritative schema

[`quarantine-attestation-schema.json`](quarantine-attestation-schema.json) is the only authoritative list of controls. The shared preflight loads it directly. A valid attestation must set every `required_controls` entry to the boolean value `true`; optional metadata never converts a failed control into a pass.

The shipped example is a complete, synthetic attestation. Copy it outside the untrusted project to `.repoquarantine.json` and complete it from independently verified sandbox facts. Do not commit the attestation: it can reveal infrastructure details.

## Output

The preflight emits JSON to stdout only.

- Exit `0` and `decision: ALLOW_READ_ONLY`: every schema control is attested.
- Exit `2` and `decision: BLOCKED`: the file is missing, malformed, non-object, or has one or more false/missing controls.

The result permits **read-only review only**. Installation, builds, tests, project scripts, browser automation, migrations, deployments, and external changes remain blocked until separately explained and explicitly approved under root `AGENTS.md`.

## Agent adapters

- `agents/hermes/SKILL.md`
- `agents/claude-code/SKILL.md`
- `agents/codex/AGENTS.md`

Adapters contain discovery and host-install guidance only. They invoke the exact same preflight command and defer all behavioural rules to root `AGENTS.md`.
