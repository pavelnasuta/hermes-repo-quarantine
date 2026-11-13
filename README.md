# Hermes RepoQuarantine

> **Zero-trust sandbox workflow for untrusted code.**

[![Validate](https://github.com/pavelnasuta/hermes-repo-quarantine/actions/workflows/validate.yml/badge.svg)](https://github.com/pavelnasuta/hermes-repo-quarantine/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Hermes RepoQuarantine** is a reusable zero-trust workflow for [Hermes Agent](https://github.com/NousResearch/hermes-agent), Claude Code, and Codex. It treats code, README files, project instructions, CI, issue text, skills, plugins, and MCP configuration as untrusted input.

It does **not** claim to detect malware. Instead, it makes the safe path explicit: whole-process isolation first, read-only review before execution, narrow egress, no host secrets, and a clear incident response path.

## Why it exists

A coding agent can be manipulated by repository content long before it runs a suspicious command. Approval dialogs, output redaction, and pattern matching reduce accidents; they are not containment. Hermes documents OS-level isolation as the boundary against adversarial model output.

RepoQuarantine turns that principle into a repeatable workflow for repository review, dependency inspection, controlled execution, and suspected compromise.

## Install

```bash
hermes skills tap add pavelnasuta/hermes-repo-quarantine
hermes skills install pavelnasuta/hermes-repo-quarantine/skills/hermes-repo-quarantine
```

Then ask Hermes, for example:

> Review this unfamiliar repository. Do not run it until the isolation boundary is verified.

## Use with Claude Code and Codex

This repository has one shared safety contract and thin host adapters. Clone it beside your work, then keep the canonical files available to the agent:

- **Hermes:** install the self-contained portable bundle above. It includes the same attestation gate and schema because a repository-tap install does not carry root-level files.
- **Claude Code:** copy or link [`agents/claude-code/SKILL.md`](agents/claude-code/SKILL.md) into `.claude/skills/hermes-repo-quarantine/SKILL.md` and retain the cloned repository for `AGENTS.md`, `specs/`, and `scripts/`.
- **Codex:** copy [`agents/codex/AGENTS.md`](agents/codex/AGENTS.md) into the target repository’s `AGENTS.md`, or merge it with existing project guidance. Keep the cloned RepoQuarantine repository available as the source of the shared contract and preflight.

Before any agent reads target-repository content, copy the example attestation outside the target repository, independently verify the sandbox controls, and run:

```bash
python scripts/quarantine_preflight.py --format json --attestation .repoquarantine.json
```

A passing preflight means **read-only review only**. It does not authorise package installation, tests, builds, scripts, deployments, plugins, MCP servers, or browser automation.

## What the skill enforces

- **No host-session work for untrusted repositories.** It requires a disposable, whole-process sandbox before reading project content.
- **Read before run.** Initial review is limited to file search and reading; no package manager, build, test, project script, or browser execution.
- **Explicit execution gates.** Each install, build, test, migration, or deployment needs a fresh explanation and user approval.
- **No ambient secrets.** The sandbox must not expose a host home directory, Docker socket, SSH agent, browser profile, cloud configuration, or production credentials.
- **Controlled egress.** Network access is off by default or allowlisted by endpoint.
- **Separate review for skills, plugins, and MCP.** They are treated as executable, in-process code—not as harmless documentation.
- **Incident mode.** Unexpected behavior stops work, disables egress, preserves non-secret evidence, and destroys the disposable environment.

## Before you use it

RepoQuarantine requires a real containment boundary. For untrusted content, Hermes recommends **whole-process wrapping**: the Hermes process, terminal, file tools, code execution, MCP subprocesses, plugins, hooks, and skills must all live inside the same disposable sandbox.

A terminal-only Docker backend is useful for shell containment, but it does not contain all in-process paths. Do not represent it as full protection.

Recommended baseline:

- run as a non-root user;
- use a separate, disposable Hermes data directory;
- do not mount a host home directory, Docker socket, SSH agent, browser state, cloud configuration, or production credentials;
- mount only the work directory, read-only at first;
- block egress or route it through an endpoint allowlist;
- apply CPU, memory, disk, and process limits;
- destroy the sandbox after the task.

## What it reviews

The first pass asks the agent to look for:

- dependency manifests, lockfiles, and lifecycle hooks;
- build/test scripts, shell scripts, Makefiles, Docker files, and dev containers;
- CI workflows, Git hooks, deploy configuration, and infrastructure code;
- credential loading, telemetry, webhooks, and network destinations;
- repository-provided skills, plugins, hooks, and MCP servers;
- instructions that attempt to override the user’s request or security boundary.

## Non-goals

- This repository is **not** a sandbox, antivirus scanner, or malware classifier.
- It cannot make a poorly configured container safe.
- It does not silently install third-party plugins, skills, or MCP servers.
- It does not rotate, revoke, or delete credentials without explicit approval.

## Verification

The repository includes an offline validator and scenario tests:

```bash
python -m unittest discover -s tests -v
python scripts/validate.py
```

The validator checks the public package contract, install commands, required files, private-path/secret patterns, and retired identifiers.

## Security and privacy

Read [SECURITY.md](SECURITY.md) before reporting a problem. Do not include tokens, private keys, credentials, or customer data in public issues.

The trust-model sources used by this skill are listed in [`references/trust-model.md`](skills/hermes-repo-quarantine/references/trust-model.md).

## Contributing

Issues and pull requests are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md). Changes to the security posture should include an evaluation scenario and should not weaken the whole-process-isolation requirement without evidence from Hermes documentation.

## License

[MIT](LICENSE) © 2026 Pavel Nasuta.
