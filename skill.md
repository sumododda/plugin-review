---
name: review-plugin
description: Use when evaluating a plugin, MCP server, skill, or extension for security risks before approving it for use with AI coding agents
---

# review-plugin

5 subagents analyze 13 security dimensions in parallel, score 79 items, produce a markdown report with APPROVE / CONDITIONAL / DENY.

## When to Use

- Evaluating a new plugin/MCP server before installing
- Re-reviewing after major version update or maintainer change
- Auditing against org security policy (`review-policy.json`)

**Not for:** reviewing your own code (use code-review instead)

## Prerequisites

`trivy` (`brew install trivy`), `git`, `gh`

## Quick Reference

| Agent | Dimensions | Reads |
|---|---|---|
| manifest-auditor | D3 Supply Chain, D11 License, Phase 0 Blockers | Manifests, lockfiles, LICENSE, Trivy output |
| code-scanner | D1 Secrets, D2 SAST | Source code, config files, git history |
| permissions-runtime-scanner | D4 Permissions, D8 Runtime | Source code, Dockerfiles, sandbox configs |
| network-mcp-scanner | D5 MCP/AI, D6 Network, D7 Data/Privacy | Source code, tool descriptions, configs |
| ci-governance | D9 CI/CD, D10 Repo Health, D12 Ops/Docs | Workflows, git history, README, CHANGELOG |

## Orchestration

### Step 1: Clone and detect

```bash
REPO_NAME=$(echo "$REPO_URL" | sed 's|.*/||' | sed 's|\.git$||')
CLONE_DIR="/tmp/plugin-review-$REPO_NAME"
rm -rf "$CLONE_DIR" && git clone --depth=100 "$REPO_URL" "$CLONE_DIR"
```

Detect ecosystem: `package.json` (Node), `pyproject.toml` (Python), `go.mod` (Go), `Cargo.toml` (Rust).

### Step 2: Run Trivy

```bash
mkdir -p "$CLONE_DIR/artifacts"
trivy fs --format json -o "$CLONE_DIR/artifacts/trivy-vulns.json" "$CLONE_DIR"
trivy fs --scanners license --format json -o "$CLONE_DIR/artifacts/trivy-licenses.json" "$CLONE_DIR"
```

Skip if trivy unavailable -- score SUP-02 and LIC-02 as N/A.

### Step 3: Read policy and dispatch

1. Read `review-policy.json` from this skill's directory
2. Read each prompt from `prompts/` directory: `manifest-auditor.md`, `code-scanner.md`, `permissions-runtime-scanner.md`, `network-mcp-scanner.md`, `ci-governance.md`
3. Replace `{CLONE_DIR}`, `{REPO_URL}`, `{ECOSYSTEM}`, and `{POLICY_*}` placeholders with actual values
4. Dispatch all 5 agents in a **single message** (parallel)

### Step 4: Score and report

Collect findings. For each dimension: `weighted = (avg_score / 5) * weight`. Sum for aggregate out of 96 (D13 is N/A), scale to 100.

**Decision logic:**
- Phase 0 blocker or hard-fail gate triggered -> DENY
- Aggregate < 70 or any High-severity item < 3 -> DENY or CONDITIONAL
- Aggregate >= 85 and no item below 3 -> APPROVE

**Hard-fail gates:** SEC-01 < 5, SUP-02 critical CVE, MCP-01 scores 0-1, PRM-06 scores 0-1, RUN-01 scores 0-1.

Write report to `reviews/{repo-name}-{date}.md` using template from `prompts/report-template.md`.

## Common Mistakes

- **Forgetting to replace placeholders** -- agents get literal `{CLONE_DIR}` and grep fails silently
- **Not reading policy file** -- agents skip org-specific blocked deps/licenses
- **Running agents sequentially** -- must dispatch all 5 in one message for parallel execution
- **Scoring D13** -- Dynamic Testing is always N/A for static review, exclude from aggregate

## Dimension Weights

| D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | D13 |
|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|
| 10 | 8  | 13 | 9  | 13 | 8  | 7  | 7  | 7  | 5   | 4   | 5   | N/A |
