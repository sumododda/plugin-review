# Review Plugin Repo

This repository contains the `review-plugin` security review workflow. Treat it as prompt and report infrastructure, not as an application with a runtime entrypoint.

## Working Agreements

- Use `skill.md`, `unified-checklist.md`, and `prompts/` together when reviewing another repository.
- Write generated review reports to `reviews/`. That directory is gitignored and review outputs should not be committed or pushed.
- Run `python3 scripts/validate-skill.py` only when changing the skill itself: `skill.md`, `README.md`, `unified-checklist.md`, `prompts/`, or `scripts/validate-skill.py`.
- Keep checklist counts, placeholders, risk logic, and report template details aligned across the repo when editing the skill.

## Delegation

- Use `manifest-auditor` for dependencies, licenses, install scripts, CVEs, and baseline checks.
- Use `code-scanner` for secrets, hardcoded credentials, dangerous patterns, and code-level trust boundaries.
- Use `permissions-runtime-scanner` for sensitive path access, subprocess behavior, human confirmation, and sandboxing.
- Use `network-mcp-scanner` for tool descriptions, MCP security, network destinations, tunneling, telemetry, and data handling.
- Use `ci-governance` for workflow hardening, maintainer trust, branch protection, and operational documentation.
- For broad audits, dispatch all five in parallel and synthesize them using the weighting and risk logic from `skill.md`.
- Let subagents search the web when they need to identify an unfamiliar package, domain, tunnel provider, or service for the final report.
- Lead with evidence and file references. Avoid style-only comments unless they hide a real risk.

## Repo Landmarks

- `skill.md`: review orchestration contract
- `unified-checklist.md`: canonical checklist, severity, and critical-flag eligibility
- `prompts/`: specialized review prompts
- `reviews/`: generated reports, ignored by git
- `scripts/validate-skill.py`: maintainer-only drift checker
