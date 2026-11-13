# RepoQuarantine adapter for Codex

Copy or merge this file into the target repository’s `AGENTS.md`, while keeping the RepoQuarantine repository available. Root RepoQuarantine `AGENTS.md` is the canonical safety contract.

From that clone, run the common gate before touching a target repository:

```bash
python scripts/quarantine_preflight.py --format json --attestation .repoquarantine.json
```

Interpret the result and choose every subsequent action only through root RepoQuarantine `AGENTS.md`.
