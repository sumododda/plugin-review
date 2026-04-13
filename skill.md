---
name: review-plugin
description: Use when evaluating a plugin, MCP server, skill, or extension for security risks before approving it for use with AI coding agents
---

# review-plugin

5 subagents analyze 12 scored security dimensions plus 1 static-review-only dimension (D13), review 76 checklist items in parallel, and produce a markdown report with APPROVE / CONDITIONAL / DENY.

## When to Use

- Evaluating a new plugin/MCP server before installing
- Re-reviewing after major version update or maintainer change
- Auditing against org security policy (`review-policy.json`)

**Not for:** reviewing your own code (use code-review instead)

## Prerequisites

Required: `git`

Recommended: `trivy` (`brew install trivy`), `gh`

Local helper: `python3` (for `scripts/validate-skill.py`)

## Canonical Sources

- `unified-checklist.md` is the source of truth for checklist IDs, default severity, and hard-fail eligibility
- `review-policy.json` is the source of truth for org-specific deny/warn rules
- `prompts/report-template.md` is the source of truth for the final report layout

## Quick Reference

| Agent | Dimensions | Reads |
|---|---|---|
| manifest-auditor | D3 Supply Chain, D11 License, Phase 0 Blockers | Manifests, lockfiles, LICENSE, Trivy output |
| code-scanner | D1 Secrets, D2 SAST | Source code, config files, git history |
| permissions-runtime-scanner | D4 Permissions, D8 Runtime | Source code, Dockerfiles, sandbox configs |
| network-mcp-scanner | D5 MCP/AI, D6 Network, D7 Data/Privacy | Source code, tool descriptions, configs |
| ci-governance | D9 CI/CD, D10 Repo Health, D12 Ops/Docs | Workflows, git history, README, CHANGELOG |

## Scoring Model

Use the same rubric across all subagents:

- `5` = strong control, verified by direct evidence
- `4` = good control with minor gaps
- `3` = partial coverage or unclear implementation
- `2` = weak control or significant gaps
- `1` = control mostly absent
- `0` = critical failure
- `N/A` = capability truly absent or cannot be assessed with static review

Evidence labels:

- `VERIFIED` = direct code, config, manifest, or history evidence
- `POTENTIAL` = heuristic signal that still needs human confirmation
- `NO` = checked and not found
- `N/A` = not applicable to this repository

Only `VERIFIED` Phase 0 blockers or hard-fail gates can force a `DENY`.

## Orchestration

### Step 1: Clone and detect

```bash
REPO_SLUG=$(echo "$REPO_URL" | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')
OWNER=${REPO_SLUG%/*}
REPO=${REPO_SLUG##*/}
CLONE_DIR=$(mktemp -d "/tmp/plugin-review-${REPO}-XXXXXX")
git clone "$REPO_URL" "$CLONE_DIR"
```

Use a full clone. Several checks rely on commit history, contributor history, and deleted-file history.

Detect ecosystem: `package.json` (Node), `pyproject.toml` (Python), `go.mod` (Go), `Cargo.toml` (Rust).

### Step 2: Run Trivy (if available)

```bash
mkdir -p "$CLONE_DIR/artifacts"
trivy fs --format json -o "$CLONE_DIR/artifacts/trivy-vulns.json" "$CLONE_DIR" || true
trivy fs --scanners license --format json -o "$CLONE_DIR/artifacts/trivy-licenses.json" "$CLONE_DIR" || true
```

If `trivy` is unavailable, score `SUP-02` and `LIC-02` as `N/A` and call out the limitation in the final report.

### Step 3: Read policy, checklist, and dispatch

1. Read `review-policy.json` and `unified-checklist.md` from this skill's directory
2. Read each prompt from `prompts/` directory: `manifest-auditor.md`, `code-scanner.md`, `permissions-runtime-scanner.md`, `network-mcp-scanner.md`, `ci-governance.md`
3. Replace `{CLONE_DIR}`, `{REPO_URL}`, `{ECOSYSTEM}`, `{OWNER}`, `{REPO}`, and the relevant `{POLICY_*}` placeholders with actual values
4. Render policy fragments as compact, human-readable lists:
   - `{POLICY_BLOCKED_CAPABILITIES}`: category, reason, packages, patterns
   - `{POLICY_BLOCKED_LICENSES_DENY}` / `{POLICY_BLOCKED_LICENSES_WARN}`: preserve SPDX identifiers
   - `{POLICY_BLOCKED_PATTERNS}`: merged pattern list across blocked capability categories
   - `{POLICY_BLOCKED_CAPABILITIES_TUNNELING}`: tunneling-focused subset used by the network scanner
   - `{POLICY_BLOCKED_NETWORK}` / `{POLICY_SENSITIVE_PATHS}`: preserve category names
   - `{POLICY_REQUIRED_FILES_HARD}` / `{POLICY_REQUIRED_FILES_SOFT}`: preserve required filenames
   - `{POLICY_INSTALL_SCRIPTS_FLAG}` / `{POLICY_MAX_DIRECT_DEPS}` / `{POLICY_MAX_TOTAL_DEPS}`: preserve raw policy values
5. Dispatch all 5 agents in a **single message** (parallel)

### Step 4: Score and report

1. Normalize outputs. Expect Phase 0 blockers as `PASS` / `FAIL` and hard-fail gates as `VERIFIED` / `POTENTIAL` / `NO`.
2. For each scored dimension: `weighted = (avg_score / 5) * weight`
3. Sum the 12 scored dimensions for an aggregate out of `96`, then scale to `100`

**Decision logic:**

- Any Phase 0 blocker `FAIL` -> `DENY`
- Any hard-fail gate `VERIFIED` -> `DENY`
- Any hard-fail gate `POTENTIAL` -> `CONDITIONAL` until disproven by human review
- Aggregate `< 70` -> `DENY`
- Aggregate `70-84` -> `CONDITIONAL`
- Aggregate `>= 85` and every non-`N/A` item is `>= 3` -> `APPROVE`
- Aggregate `>= 85` with any non-`N/A` item `< 3` -> `CONDITIONAL`

**Hard-fail gates:** `SEC-01` verified secret, `SUP-02` unmitigated critical CVE in the shipped/default install path, `MCP-01` verified malicious prompt injection in tool descriptions, `PRM-06` destructive operation without meaningful human confirmation, `RUN-01` privileged/root execution by default without strong justification.

Write report to `reviews/{repo-name}-{date}.md` using template from `prompts/report-template.md`.

### Step 5: Validate the skill itself

Run `python3 scripts/validate-skill.py` after editing this repo so checklist counts, placeholders, and templates stay aligned.

## Common Mistakes

- **Forgetting to replace placeholders** -- agents get literal `{CLONE_DIR}` and grep fails silently
- **Not reading policy or checklist files** -- agents skip org-specific rules or drift from the canonical item list
- **Using a shallow clone** -- history-based checks become incomplete or misleading
- **Running agents sequentially** -- must dispatch all 5 in one message for parallel execution
- **Treating regex hits as auto-deny** -- hard-fail gates require `VERIFIED` evidence, not just a grep match
- **Scoring D13** -- Dynamic Testing is always `N/A` for static review, exclude from aggregate

## Dimension Weights

| D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | D13 |
|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|
| 10 | 8  | 13 | 9  | 13 | 8  | 7  | 7  | 7  | 5   | 4   | 5   | N/A |
