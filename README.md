# review-plugin

Security review skill for AI agent plugins, MCP servers, and extensions. Dispatches 5 parallel subagents to analyze a GitHub repository across 12 scored security dimensions plus 1 static-review-only dimension, reviews 76 checklist items, and generates a markdown report with a score, risk level, and flagged findings.

## How It Works

```text
/review-plugin https://github.com/org/some-mcp-server
```

1. Clones the repo with full history
2. Runs Trivy (CVE + license scan) if available
3. Reads the canonical checklist (`unified-checklist.md`) and the five specialized review prompts
4. Dispatches 5 parallel review agents:

| Agent | What it checks |
|---|---|
| **manifest-auditor** | Dependencies, supply chain, licenses, baseline checks |
| **code-scanner** | Secrets, dangerous code patterns |
| **permissions-runtime-scanner** | Permissions, execution scope, runtime sandboxing |
| **network-mcp-scanner** | MCP/AI security, network destinations, data handling |
| **ci-governance** | CI/CD hardening, repo health, documentation quality |

5. Scores each dimension (weighted, 100-point scale)
6. Writes report to `reviews/<plugin-name>-<date>.md`, including a full dependency-and-license appendix for direct and transitive dependencies when identifiable

## Prerequisites

```bash
brew install trivy    # recommended: CVE + license scan
brew install gh       # recommended: repo metadata and branch protection
python3 --version     # used by scripts/validate-skill.py
```

## What Gets Flagged

The skill is designed to flag and explain risky patterns rather than enforce a local deny list. Typical findings include:

- tunnel services, remote-shell features, or unusual public network exposure
- suspicious install scripts or remote code execution during setup
- copyleft, source-available, or otherwise noteworthy license terms
- sensitive path access, broad process spawning, or weak runtime isolation
- telemetry, data exfiltration patterns, or missing security documentation

When a package, domain, tunnel provider, or vendor service is unfamiliar, subagents may search the web or vendor docs to identify what it is and summarize why it matters in the report.

The final report is also expected to include:

- all direct dependencies with versions
- all transitive dependencies that can be identified from lockfiles or scanner output
- a license value for each dependency when available, otherwise `unknown`

## Scoring

| Risk Level | Score | Conditions |
|---|---|---|
| **LOW** | >= 85 | Every non-N/A item scores at least 3 and no critical flag is verified |
| **MEDIUM** | 70-84 | Or any critical flag is only a potential signal pending human review |
| **HIGH** | < 70 | Or any critical flag is verified |

Critical flags require `VERIFIED` evidence, not just a regex hit. The current critical-flag set is:

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

- `unified-checklist.md` is the source of truth for checklist IDs, default severity, and critical-flag eligibility
- `prompts/report-template.md` is the source of truth for final report layout

## Validation

Run the validator after editing the skill:

```bash
python3 scripts/validate-skill.py
```

## Repo-Local Agent Setup

This repo now includes project-local agent scaffolding for Codex, Claude Code, and OpenCode:

- `AGENTS.md` is the shared repo guidance for Codex and OpenCode
- `CLAUDE.md` mirrors the key repo instructions for Claude Code
- `.codex/agents/` defines one subagent per review prompt
- `.claude/agents/` defines one subagent per review prompt
- `.opencode/agents/` defines one subagent per review prompt
- `opencode.json` allows the built-in `build` and `plan` agents, plus a custom `review-lead` primary agent, to delegate to those subagents
- task subagents may search the web when they need to identify an unfamiliar package, domain, tunnel provider, or service for the final report

The current subagents map directly to the prompt files:

- `manifest-auditor`
- `code-scanner`
- `permissions-runtime-scanner`
- `network-mcp-scanner`
- `ci-governance`

Codex note: as of April 14, 2026, the official Codex docs say custom subagents are available but are not spawned automatically. This repo config makes the agents available and sets sensible limits, but you still need an explicit ask such as:

```text
Review this repo with parallel subagents. Spawn manifest-auditor, code-scanner, permissions-runtime-scanner, network-mcp-scanner, and ci-governance, then summarize the findings.
```

Claude Code and OpenCode can auto-delegate more aggressively based on the subagent descriptions in this repo.

## File Structure

```text
AGENTS.md                   # Shared repo guidance for Codex/OpenCode
CLAUDE.md                   # Shared repo guidance for Claude Code
.codex/
  config.toml               # Codex multi-agent limits
  agents/
    manifest-auditor.toml
    code-scanner.toml
    permissions-runtime-scanner.toml
    network-mcp-scanner.toml
    ci-governance.toml
.claude/
  agents/
    manifest-auditor.md
    code-scanner.md
    permissions-runtime-scanner.md
    network-mcp-scanner.md
    ci-governance.md
.opencode/
  agents/
    manifest-auditor.md
    code-scanner.md
    permissions-runtime-scanner.md
    network-mcp-scanner.md
    ci-governance.md
opencode.json               # OpenCode agent permissions and primary review agent
skill.md                    # Skill orchestrator (loaded by AI agent)
unified-checklist.md        # Full 76-item canonical checklist
reviews/                    # Generated reports
scripts/
  validate-skill.py         # Drift checker for counts, placeholders, and templates
prompts/
  manifest-auditor.md       # Subagent: deps, licenses, baseline checks
  code-scanner.md           # Subagent: secrets and SAST
  permissions-runtime-scanner.md
  network-mcp-scanner.md    # Subagent: MCP, network, data
  ci-governance.md          # Subagent: CI/CD, repo health, docs
  report-template.md        # Report output template
```

## License

MIT
