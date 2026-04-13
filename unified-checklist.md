# Unified Checklist

This file is the canonical list of scored review items for `review-plugin`.

- Default severity can be raised or lowered when the repository evidence justifies it.
- Hard-fail gates only trigger when the finding status is `VERIFIED`.
- `D13: Dynamic Testing & Fuzzing` has no checklist items in this skill and is always `N/A` for static review.

## D1: Secrets & Credential Security

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| SEC-01 | Secret patterns in code and history | Critical | Yes |
| SEC-02 | No hardcoded secrets | High | No |
| SEC-03 | Secure credential storage | High | No |
| SEC-04 | Safe logging | Medium | No |
| SEC-05 | OAuth flow security | High | No |
| SEC-06 | Token management | Medium | No |

## D2: Static Code Analysis

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| SCA-01 | Dangerous patterns | High | No |
| SCA-02 | Arbitrary code execution | Critical | No |
| SCA-03 | Trust boundary review | High | No |
| SCA-04 | Binary artifacts | Medium | No |

## D3: Dependency & Supply Chain

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| SUP-01 | Dependency inventory | Medium | No |
| SUP-02 | Known CVEs | Critical | Yes |
| SUP-03 | Lockfile integrity | High | No |
| SUP-04 | Version pinning | Medium | No |
| SUP-05 | Typosquatting | High | No |
| SUP-06 | Install scripts | High | No |
| SUP-07 | Obfuscated code | High | No |
| SUP-08 | Dependency count | Low | No |

## D4: Permissions & Execution Scope

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| PRM-01 | Least privilege | High | No |
| PRM-02 | Filesystem scoping | High | No |
| PRM-03 | Process spawning | High | No |
| PRM-04 | Credential store access | Medium | No |
| PRM-05 | Scope expansion on update | Medium | No |
| PRM-06 | Human-in-the-loop | Critical | Yes |

## D5: AI Agent & MCP-Specific Security

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| MCP-01 | Prompt injection in tool descriptions | Critical | Yes |
| MCP-02 | Output sanitization | High | No |
| MCP-03 | Input trust boundaries | High | No |
| MCP-04 | Tool description integrity | Medium | No |
| MCP-05 | Auto-approval | High | No |
| MCP-06 | Cross-model trust | Medium | No |
| MCP-07 | Tool scope | High | No |
| MCP-08 | Sampling feature | Medium | No |
| MCP-09 | Context isolation | High | No |
| MCP-10 | Server authentication | High | No |

## D6: Network & External Interactions

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| NET-01 | Network destinations | High | No |
| NET-02 | SSRF protection | High | No |
| NET-03 | DNS exfiltration | Medium | No |
| NET-04 | Localhost binding | Medium | No |
| NET-05 | Tunnel creation | High | No |
| NET-06 | Rate limiting | Medium | No |

## D7: Data Handling & Privacy

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| DAT-01 | Data inventory | Medium | No |
| DAT-02 | Telemetry | Medium | No |
| DAT-03 | TLS bypass | Critical | No |
| DAT-04 | Exfiltration patterns | High | No |
| DAT-05 | User consent | Medium | No |
| DAT-06 | Data retention | Medium | No |
| DAT-07 | Log leakage | High | No |

## D8: Runtime Sandboxing & Isolation

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| RUN-01 | Minimal privileges | Critical | Yes |
| RUN-02 | Filesystem/process isolation | High | No |
| RUN-03 | Resource limits | Medium | No |
| RUN-04 | Container/sandbox config | Medium | No |
| RUN-05 | Workspace trust model | High | No |

## D9: Build, CI/CD & Release Integrity

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| BLD-01 | CI workflow hardening | High | No |
| BLD-02 | CI secrets safety | High | No |
| BLD-03 | Artifact provenance | Medium | No |
| BLD-04 | Reproducible builds | Medium | No |
| BLD-05 | Version pinning and updates | Low | No |

## D10: Repository Health & Maintainer Trust

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| REP-01 | Maintainer identity | Medium | No |
| REP-02 | Active maintenance | Medium | No |
| REP-03 | Bus factor | Low | No |
| REP-04 | Established history | Low | No |
| REP-05 | AI-authored code | Medium | No |
| REP-06 | Marketplace verification | Medium | No |
| REP-07 | Branch protection | High | No |

## D11: Licensing & Legal Compliance

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| LIC-01 | License declared | Medium | No |
| LIC-02 | Dependency licenses | High | No |
| LIC-03 | Third-party notices | Low | No |
| LIC-04 | Export controls | Low | No |

## D12: Operational Security & Documentation

| ID | Title | Default Severity | Hard-Fail Gate |
|---|---|---|---|
| OPS-01 | SECURITY.md | Medium | No |
| OPS-02 | README security docs | Medium | No |
| OPS-03 | Changelog | Low | No |
| OPS-04 | Incident response | Medium | No |
| OPS-05 | Rollback/kill switch | Medium | No |
| OPS-06 | CI security gates | High | No |
| OPS-07 | Audit logging | Medium | No |
| OPS-08 | SIEM integration | Low | No |

## D13: Dynamic Testing & Fuzzing

This dimension is outside the scope of this static-review skill. Always report `N/A` and exclude it from the aggregate score.
