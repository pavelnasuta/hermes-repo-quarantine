# Trust model basis

This skill follows Hermes Agent's documented security posture rather than treating prompting or approval UI as a containment boundary.

## Primary rule

The Hermes Agent Security Policy states that **OS-level isolation is the only security boundary against an adversarial LLM**. Approval gates, output redaction, pattern scanners, and allowlists are in-process heuristics and must not be represented as a sandbox.

## Isolation choices

- A terminal backend can confine shell and file-tool operations, but it does not confine code execution, MCP subprocesses, plugins, hooks, or skill loading that stay in the agent process.
- Whole-process wrapping places the full Hermes process tree inside the same OS-level sandbox. This is the documented posture for untrusted content surfaces and shared/production deployments.

## Deployment rules used by this skill

- Run the agent as a non-root user.
- Keep host home directories, Docker sockets, browser state, SSH agents, and production credentials out of the sandbox.
- Use a separate data directory; never share the primary Hermes data volume with the quarantine agent.
- Restrict egress. Docker's default host networking permits arbitrary outbound traffic. Use an internal network plus an allowlisted egress proxy when network access is necessary.
- Treat third-party skills and plugins as executable in-process code and review them before installation.

## Sources

- https://github.com/NousResearch/hermes-agent/security/policy
- https://hermes-agent.nousresearch.com/docs/user-guide/docker
- https://hermes-agent.nousresearch.com/docs/user-guide/egress/network-isolation

These sources describe the security boundary and deployment primitives. They do not guarantee safety for an operator who grants a sandbox sensitive mounts, broad network egress, or privileged credentials.
