# review-plugin

Security review skill for AI agent plugins, MCP servers, and extensions. Dispatches 4 parallel subagents to analyze a GitHub repository across 13 security dimensions, scores 79 checklist items, and generates a markdown report with an APPROVE / CONDITIONAL / DENY decision.

## How It Works

```
/review-plugin https://github.com/org/some-mcp-server
```

1. Clones the repo
2. Runs Trivy (CVE + license scan)
3. Reads your org policy (`review-policy.json`)
4. Dispatches 4 parallel review agents:

| Agent | What it checks |
|---|---|
| **manifest-auditor** | Dependencies, supply chain, licenses, critical blockers |
| **code-scanner** | Secrets, dangerous code patterns, permissions, runtime safety |
| **network-mcp-scanner** | MCP/AI security, network destinations, data handling |
| **ci-governance** | CI/CD hardening, repo health, documentation quality |

5. Scores each dimension (weighted, 100-point scale)
6. Writes report to `reviews/<plugin-name>-<date>.md`

## Prerequisites

```bash
brew install trivy    # only external tool needed
brew install gh       # recommended, for repo metadata
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
| **APPROVE** | >= 85 | No hard-fail gates, no High-severity item below 3 |
| **CONDITIONAL** | 70-84 | Remediation plan required within 30 days |
| **DENY** | < 70 | Or any hard-fail gate triggered |

**Hard-fail gates**: verified secrets found, unmitigated critical CVE, prompt injection in tool descriptions, no human-in-the-loop for destructive ops, privileged execution without justification.

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

## File Structure

```
skill.md                    # Skill orchestrator (loaded by AI agent)
review-policy.json          # Org security policy config
unified-checklist.md        # Full 79-item reference checklist
reviews/                    # Generated reports
prompts/
  manifest-auditor.md       # Subagent prompt: deps, licenses, blockers
  code-scanner.md           # Subagent prompt: secrets, SAST, permissions
  network-mcp-scanner.md    # Subagent prompt: MCP, network, data
  ci-governance.md          # Subagent prompt: CI/CD, repo health, docs
  report-template.md        # Report output template
```

## License

MIT
