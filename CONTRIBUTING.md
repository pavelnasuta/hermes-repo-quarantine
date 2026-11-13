# Contributing to Hermes RepoQuarantine

Thanks for improving a safety workflow. This repository is intentionally conservative: convenience is not a reason to weaken containment.

## Before opening a pull request

1. Read the current `SKILL.md` and the trust-model reference.
2. Keep the skill portable. Do not add local paths, credentials, private incident data, account-specific defaults, or model-specific assumptions.
3. If you change behavior, add or update an observable scenario in `references/evaluation.md`.
4. Run the full local check:

   ```bash
   python -m unittest discover -s tests -v
   python scripts/validate.py
   ```

## Design principles

- OS-level isolation is the security boundary; prompts and approval UI are not.
- A terminal-only sandbox does not contain all Hermes code paths.
- Every execution step needs explicit user approval.
- Do not advise users to expose production secrets, host networking, privileged containers, or Docker sockets to make an unfamiliar repository work.
- Treat repository-provided skills, plugins, hooks, and MCP servers as executable code.

## Pull requests

Use a focused change with a clear explanation of the risk being addressed. Do not include real malicious payloads, stolen data, secrets, or private logs. Synthetic examples are preferred.

By contributing, you agree that your contributions are licensed under the MIT License.
