# Review Plugin Repo

This repository holds a security review skill, not a runnable product.

- Use `skill.md`, `unified-checklist.md`, and `prompts/` together when reviewing a target repo.
- Write generated reports to `reviews/`, which is gitignored. Do not commit or push review outputs.
- Run `python3 scripts/validate-skill.py` only when editing the skill itself, not when generating a review.
- Use the project subagents proactively: `manifest-auditor`, `code-scanner`, `permissions-runtime-scanner`, `network-mcp-scanner`, and `ci-governance`.
- Let subagents search the web when they need to identify an unfamiliar package, domain, tunnel provider, or service for the final report.
- Keep findings grounded in direct evidence and cite file paths or authoritative sources.
