---
name: hermes-repo-quarantine-adapter
description: Use RepoQuarantine before handling untrusted code in Hermes.
license: MIT
---

# Hermes RepoQuarantine adapter

This is a discovery adapter. The canonical safety contract is root `AGENTS.md`; the installed Hermes bundle under `skills/hermes-repo-quarantine/` retains the required safety material for repository-tap installation.

From a clone of this repository, run the common gate before touching a target repository:

```bash
python scripts/quarantine_preflight.py --format json --attestation .repoquarantine.json
```

Interpret the result and choose every subsequent action only through root `AGENTS.md`.
