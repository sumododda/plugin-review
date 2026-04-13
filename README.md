# review-plugin

Security review skill for AI agent plugins, MCP servers, and extensions. Dispatches 5 parallel subagents to analyze a GitHub repository across 12 scored security dimensions plus 1 static-review-only dimension, reviews 76 checklist items, and generates a markdown report with an APPROVE / CONDITIONAL / DENY decision.

## How It Works

```text
/review-plugin https://github.com/org/some-mcp-server
```

1. Clones the repo with full history
2. Runs Trivy (CVE + license scan) if available
3. Reads your org policy (`review-policy.json`) and the canonical checklist (`unified-checklist.md`)
4. Dispatches 5 parallel review agents:

| Agent | What it checks |
|---|---|
| **manifest-auditor** | Dependencies, supply chain, licenses, critical blockers |
| **code-scanner** | Secrets, dangerous code patterns |
| **permissions-runtime-scanner** | Permissions, execution scope, runtime sandboxing |
| **network-mcp-scanner** | MCP/AI security, network destinations, data handling |
| **ci-governance** | CI/CD hardening, repo health, documentation quality |

5. Scores each dimension (weighted, 100-point scale)
6. Writes report to `reviews/<plugin-name>-<date>.md`

## Prerequisites

```bash
brew install trivy    # recommended: CVE + license scan
brew install gh       # recommended: repo metadata and branch protection
python3 --version     # used by scripts/validate-skill.py
```

## Org Policy

Edit `review-policy.json` to configure:

- **Blocked capabilities** -- tunneling (ngrok), remote shells, crypto mining, keyloggers, screen capture
- **Blocked licenses** -- three tiers: deny (AGPL, SSPL), warn (GPL, MPL), review (LGPL, EPL)
- **Blocked network destinations** -- exfiltration services, paste sites, IP loggers, C2 patterns
- **Install scripts** -- flagged for review (not blocked), auto-deny only if curl-pipe-to-shell
- **Dependency limits** -- max 50 direct, 300 total
- **Sensitive paths** -- ~/.ssh, ~/.aws, ~/.kube, etc.
- **Required files** -- LICENSE (hard), README/SECURITY.md/CHANGELOG (soft)

## Scoring

| Decision | Score | Conditions |
|---|---|---|
| **APPROVE** | >= 85 | No verified hard-fail gates and every non-N/A item scores at least 3 |
| **CONDITIONAL** | 70-84 | Or any hard-fail gate is only a potential signal pending human review |
| **DENY** | < 70 | Or any Phase 0 blocker fails or any hard-fail gate is verified |

Hard-fail gates require `VERIFIED` evidence, not just a regex hit. The current gate set is:

- verified secret or private key committed to the repo or history
- unmitigated critical CVE in the shipped/default install path
- verified malicious prompt injection in tool descriptions
- destructive operations without meaningful human confirmation
- privileged or root execution by default without strong justification

## 13 Security Dimensions

| # | Dimension | Weight |
|---|---|---|
| 1 | Secrets & Credential Security | 10 |
| 2 | Static Code Analysis | 8 |
| 3 | Dependency & Supply Chain | 13 |
| 4 | Permissions & Execution Scope | 9 |
| 5 | AI Agent & MCP-Specific Security | 13 |
| 6 | Network & External Interactions | 8 |
| 7 | Data Handling & Privacy | 7 |
| 8 | Runtime Sandboxing & Isolation | 7 |
| 9 | Build, CI/CD & Release Integrity | 7 |
| 10 | Repository Health & Maintainer Trust | 5 |
| 11 | Licensing & Legal Compliance | 4 |
| 12 | Operational Security & Documentation | 5 |
| 13 | Dynamic Testing & Fuzzing | N/A (static review) |

## Canonical Files

- `unified-checklist.md` is the source of truth for checklist IDs, default severity, and hard-fail eligibility
- `review-policy.json` is the source of truth for org-specific rules
- `prompts/report-template.md` is the source of truth for final report layout

## Validation

Run the validator after editing the skill:

```bash
python3 scripts/validate-skill.py
```

## File Structure

```text
skill.md                    # Skill orchestrator (loaded by AI agent)
review-policy.json          # Org security policy config
unified-checklist.md        # Full 76-item canonical checklist
reviews/                    # Generated reports
scripts/
  validate-skill.py         # Drift checker for counts, placeholders, and templates
prompts/
  manifest-auditor.md       # Subagent: deps, licenses, blockers
  code-scanner.md           # Subagent: secrets and SAST
  permissions-runtime-scanner.md
  network-mcp-scanner.md    # Subagent: MCP, network, data
  ci-governance.md          # Subagent: CI/CD, repo health, docs
  report-template.md        # Report output template
```

## License

MIT
