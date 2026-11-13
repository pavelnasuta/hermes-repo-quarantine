# Security Policy

## Reporting a vulnerability

Please do **not** open a public issue for a suspected vulnerability, exposed secret, or active exploitation path.

Use GitHub's private vulnerability reporting for this repository when it is available. If it is not available, open a minimal issue that contains no exploit details, credentials, personal data, or affected private repository information, and request a private channel.

## Scope

This repository contains a workflow skill, not a sandbox implementation. Reports are useful when they show that the skill's published instructions are materially unsafe, misleading about Hermes' documented trust model, or accidentally expose sensitive data.

## Out of scope

- Prompt-injection examples that do not lead to a concrete escape from the documented isolation posture.
- Reports that require an operator to have deliberately mounted secrets, host state, or privileged sockets into a sandbox.
- Malware submissions, private credentials, or customer data.

## Response expectations

Reports will be acknowledged when feasible. Do not rely on this project for emergency incident response: immediately stop the affected workload, restrict egress, and follow your organisation's incident process.
