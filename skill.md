---
name: review-plugin
description: Use when evaluating a plugin, MCP server, skill, or extension for security risks before using it with AI coding agents
---

# review-plugin

5 subagents analyze 12 scored security dimensions plus 1 static-review-only dimension (D13), review 76 checklist items in parallel, and produce a markdown report with a score, risk level, and flagged findings.

## When to Use

- Evaluating a new plugin/MCP server before installing
- Re-reviewing after major version update or maintainer change
- Investigating why a plugin feels risky without relying on a hardcoded local deny list

**Not for:** reviewing your own code (use code-review instead)

## Prerequisites

Required: `git`

Recommended: `trivy` (`brew install trivy`), `gh`

Local helper: `python3` (for `scripts/validate-skill.py`)

## Canonical Sources

- `unified-checklist.md` is the source of truth for checklist IDs, default severity, and critical-flag eligibility
- `prompts/report-template.md` is the source of truth for the final report layout

## Quick Reference

| Agent | Dimensions | Reads |
|---|---|---|
| manifest-auditor | D3 Supply Chain, D11 License, Baseline Checks | Manifests, lockfiles, LICENSE, Trivy output |
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

Critical flags do not auto-reject a repository. They raise the reported risk level and must be explained clearly in the final report.

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

### Step 3: Read checklist, prompts, and dispatch

1. Read `unified-checklist.md` from this skill's directory
2. Read each prompt from `prompts/` directory: `manifest-auditor.md`, `code-scanner.md`, `permissions-runtime-scanner.md`, `network-mcp-scanner.md`, `ci-governance.md`
3. Replace `{CLONE_DIR}`, `{REPO_URL}`, `{ECOSYSTEM}`, `{OWNER}`, and `{REPO}` placeholders with actual values
4. Let subagents use web research when needed to identify an unfamiliar package, domain, tunnel provider, protocol, service, or license term that materially affects the review. Prefer vendor docs or primary sources and keep the explanation concise.
5. Dispatch all 5 agents in a **single message** (parallel)

### Step 4: Score and report

1. Normalize outputs. Expect baseline checks as `PASS` / `FLAG` and critical flags as `VERIFIED` / `POTENTIAL` / `NO`.
2. For each scored dimension: `weighted = (avg_score / 5) * weight`
3. Sum the 12 scored dimensions for an aggregate out of `96`, then scale to `100`

**Risk-level logic:**

- Any critical flag `VERIFIED` -> at least `HIGH`
- Any critical flag `POTENTIAL` -> at least `MEDIUM`
- Aggregate `< 70` -> `HIGH`
- Aggregate `70-84` -> `MEDIUM`
- Aggregate `>= 85` and every non-`N/A` item is `>= 3` -> `LOW`
- Aggregate `>= 85` with any non-`N/A` item `< 3` -> `MEDIUM`

Use the highest applicable risk level. The report should help a human decide, not enforce a local blocklist.

**Critical flags:** `SEC-01` verified secret, `SUP-02` unmitigated critical CVE in the shipped/default install path, `MCP-01` verified malicious prompt injection in tool descriptions, `PRM-06` destructive operation without meaningful human confirmation, `RUN-01` privileged/root execution by default without strong justification.

Write report to `reviews/{repo-name}-{date}.md` using template from `prompts/report-template.md`.

The final report should include a full dependency and license appendix covering every dependency the review can identify. Include direct and transitive dependencies, versions when known, relationship (`direct` or `transitive`), and license. If the license cannot be determined, label it `unknown` instead of omitting the dependency.

### Step 5: Validate the skill itself

Run `python3 scripts/validate-skill.py` after editing this repo so checklist counts, placeholders, and templates stay aligned.

## Common Mistakes

- **Forgetting to replace placeholders** -- agents get literal `{CLONE_DIR}` and grep fails silently
- **Not reading the checklist or prompts** -- agents drift from the canonical item list or the expected output format
- **Using a shallow clone** -- history-based checks become incomplete or misleading
- **Running agents sequentially** -- must dispatch all 5 in one message for parallel execution
- **Treating a risky capability as automatic rejection** -- explain it in the report and let the evidence drive the score and risk level
- **Scoring D13** -- Dynamic Testing is always `N/A` for static review, exclude from aggregate

## Dimension Weights

| D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | D13 |
|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|
| 10 | 8  | 13 | 9  | 13 | 8  | 7  | 7  | 7  | 5   | 4   | 5   | N/A |
