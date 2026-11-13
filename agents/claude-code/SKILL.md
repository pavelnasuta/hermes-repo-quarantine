---
name: hermes-repo-quarantine
description: Apply RepoQuarantine before handling untrusted code.
---

# RepoQuarantine for Claude Code

Install this adapter as `.claude/skills/hermes-repo-quarantine/SKILL.md`, while keeping the RepoQuarantine repository available. Root `AGENTS.md` is the canonical safety contract.

From that clone, run the common gate before touching a target repository:

```bash
python scripts/quarantine_preflight.py --format json --attestation .repoquarantine.json
```

Interpret the result and choose every subsequent action only through root `AGENTS.md`.
