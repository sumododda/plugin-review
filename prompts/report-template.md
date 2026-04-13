# Plugin Security Review: {REPO_NAME}

## Decision: {DECISION}
## Score: {SCORE}/100

---

### Review Metadata

| Field | Value |
|---|---|
| **Repository** | {REPO_URL} |
| **Commit** | {COMMIT_SHA} |
| **Review Date** | {DATE} |
| **Ecosystem** | {ECOSYSTEM} |
| **Reviewer** | AI Security Review (automated) |

---

### Critical Blockers (Phase 0)

| ID | Check | Result |
|---|---|---|
| CB-04 | LICENSE file present | {CB04} |
| CB-05 | License compatible with org policy | {CB05} |
| CB-07 | No obfuscated code with exfiltration | {CB07} |

---

### Executive Summary

{EXECUTIVE_SUMMARY}

---

### Policy Violations

{POLICY_VIOLATIONS}

---

### Scoring Summary

| # | Dimension | Weight | Avg (0-5) | Weighted |
|---|-----------|--------|-----------|----------|
| 1 | Secrets & Credential Security | 10 | {D1_AVG} | {D1_WEIGHTED} |
| 2 | Static Code Analysis | 8 | {D2_AVG} | {D2_WEIGHTED} |
| 3 | Dependency & Supply Chain | 13 | {D3_AVG} | {D3_WEIGHTED} |
| 4 | Permissions & Execution Scope | 9 | {D4_AVG} | {D4_WEIGHTED} |
| 5 | AI Agent & MCP-Specific Security | 13 | {D5_AVG} | {D5_WEIGHTED} |
| 6 | Network & External Interactions | 8 | {D6_AVG} | {D6_WEIGHTED} |
| 7 | Data Handling & Privacy | 7 | {D7_AVG} | {D7_WEIGHTED} |
| 8 | Runtime Sandboxing & Isolation | 7 | {D8_AVG} | {D8_WEIGHTED} |
| 9 | Build, CI/CD & Release Integrity | 7 | {D9_AVG} | {D9_WEIGHTED} |
| 10 | Repository Health & Maintainer Trust | 5 | {D10_AVG} | {D10_WEIGHTED} |
| 11 | Licensing & Legal Compliance | 4 | {D11_AVG} | {D11_WEIGHTED} |
| 12 | Operational Security & Documentation | 5 | {D12_AVG} | {D12_WEIGHTED} |
| 13 | Dynamic Testing & Fuzzing | 4 | N/A | N/A |
| | **TOTAL** | | | **{SCORE}/100** |

---

### Hard-Fail Gates

| Gate | Triggered? | Evidence |
|---|---|---|
| SEC-01 < 5 (secrets found) | {GATE_SEC01} | {GATE_SEC01_EVIDENCE} |
| SUP-02 critical CVE unmitigated | {GATE_SUP02} | {GATE_SUP02_EVIDENCE} |
| MCP-01 scores 0-1 (prompt injection) | {GATE_MCP01} | {GATE_MCP01_EVIDENCE} |
| PRM-06 scores 0-1 (no HITL) | {GATE_PRM06} | {GATE_PRM06_EVIDENCE} |
| RUN-01 scores 0-1 (privileged) | {GATE_RUN01} | {GATE_RUN01_EVIDENCE} |

---

### Detailed Findings

{DETAILED_FINDINGS}

---

### Network Destinations Found

{NETWORK_DESTINATIONS}

---

### Dependency Summary

{DEPENDENCY_SUMMARY}

---

### Install Scripts

{INSTALL_SCRIPTS}

---

### MCP Tool Description Hashes

{TOOL_HASHES}

---

### Recommendations

{RECOMMENDATIONS}

---

### Re-Review Triggers

This approval expires when any of these occur:
- Major version update released
- New permissions requested
- Dependency CVE with CVSS >= 7.0
- Maintainer account change or compromise
- 90 days elapsed since this review
- MCP tool description hash changed
- Security incident in issue tracker
- License changed
