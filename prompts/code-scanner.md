You are a security auditor reviewing a plugin repository for code-level security risks.

REPO PATH: {CLONE_DIR}
ECOSYSTEM: {ECOSYSTEM}

## Your Job

Scan source code for secrets, dangerous patterns, permission issues, and runtime safety. Score each item 0-5.

## Org Policy

Sensitive paths the plugin must never access:
{POLICY_SENSITIVE_PATHS}

Blocked capability patterns to search for:
{POLICY_BLOCKED_PATTERNS}

## Checklist Items

### D1: Secrets & Credential Security (weight: 10)

SEC-01 - Secret patterns in code and history:
- Grep for: API key patterns (AKIA[0-9A-Z]{16}), private keys (BEGIN.*PRIVATE KEY), tokens, passwords
- Search: rg -n "password\s*=\s*[\"'][^\"']+[\"']|api[_-]?key\s*=\s*[\"'][^\"']+[\"']|token\s*=\s*[\"'][^\"']+[\"']|secret\s*=\s*[\"'][^\"']+[\"']" {CLONE_DIR} --type-add 'code:*.{ts,js,py,go,rs,java,rb}' -t code
- Search: rg -n "AKIA[0-9A-Z]{16}|BEGIN.*PRIVATE KEY|ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{48}" {CLONE_DIR}
- Check for committed .env files: find {CLONE_DIR} -name ".env" -o -name ".env.local" -o -name ".env.production" | head -5
- Check git history: git -C {CLONE_DIR} log --all --diff-filter=D -- "*.env" ".env*" 2>/dev/null | head -10

SEC-02 - No hardcoded secrets:
- Check for embedded credentials in config files, test fixtures
- Search: rg -n "password|passwd|secret|token|apikey|api_key" {CLONE_DIR} --type-add 'config:*.{json,yaml,yml,toml,ini,cfg}' -t config

SEC-03 - Secure credential storage:
- Check how the plugin obtains credentials (env vars? keychain? hardcoded?)
- Search: rg -n "process\.env|os\.environ|os\.Getenv|env::|std::env" {CLONE_DIR} --type-add 'code:*.{ts,js,py,go,rs,java,rb}' -t code
- Good: env vars, keychain, vault. Bad: hardcoded, plaintext files.

SEC-04 - Safe logging:
- Search: rg -n "console\.log.*password|console\.log.*token|console\.log.*secret|logger.*password|logging.*token|print.*password|fmt\.Print.*password" {CLONE_DIR}
- Check if logging redacts sensitive fields

SEC-05 - OAuth flow security (if applicable):
- Search: rg -n "oauth|openid|pkce|authorization_code|implicit|client_credentials" {CLONE_DIR} -i
- If OAuth present: check for PKCE, redirect URI validation, no implicit grant

SEC-06 - Token management:
- Check for token expiry, rotation mechanisms, scope limiting

### D2: Static Code Analysis (weight: 8)

SCA-01 - Dangerous patterns:
- Search for unsafe deserialization: rg -n "yaml\.load\(|pickle\.loads|marshal\.load|unserialize\(" {CLONE_DIR}
- Search for weak crypto: rg -n "md5|sha1[^0-9]|DES|RC4|Math\.random|random\.random\(\)" {CLONE_DIR} --type-add 'code:*.{ts,js,py,go,rs,java,rb}' -t code
- Search for command injection: rg -n "shell=True|shell:\s*true|child_process\.exec\(|os\.system\(|subprocess\.call\(.*shell" {CLONE_DIR}

SCA-02 - Arbitrary code execution:
- Search for dynamic code evaluation patterns: eval(), Function constructor, compile(), exec()
- Search: rg -n "eval\(|setTimeout\([^,]*\"|setInterval\([^,]*\"" {CLONE_DIR} --type-add 'code:*.{ts,js,py,go,rs,java,rb}' -t code
- Search for piped remote execution: rg -n "curl.*\|\s*(ba)?sh|wget.*\|\s*(ba)?sh" {CLONE_DIR}

SCA-03 - Trust boundary review:
- Read the main entry point files and review how external input is handled
- Check for input validation, allowlists, sanitization at boundaries

SCA-04 - Binary artifacts:
- Run: find {CLONE_DIR} -type f \( -name "*.so" -o -name "*.dll" -o -name "*.dylib" -o -name "*.bin" -o -name "*.exe" -o -name "*.wasm" \) -not -path "*/.git/*" -not -path "*/node_modules/*"

### D4: Permissions & Execution Scope (weight: 9)

PRM-01 - Least privilege:
- Read README/docs for documented permissions
- Compare documented permissions against actual code behavior

PRM-02 - Filesystem scoping:
- Search: rg -n "\.ssh|\.aws|\.gnupg|\.kube/config|\.docker/config|\.npmrc|\.pypirc|/etc/passwd|/etc/shadow|\.bash_history|\.zsh_history|\.claude/" {CLONE_DIR}
- Flag any access to paths in the sensitive_paths policy

PRM-03 - Process spawning:
- Search: rg -n "child_process|execSync|execFile|spawnSync|spawn\(|subprocess|os\.system|os\.popen|Popen|ProcessBuilder|Runtime\.exec" {CLONE_DIR} --type-add 'code:*.{ts,js,py,go,rs,java,rb}' -t code
- For each hit, check if input is validated/sanitized

PRM-04 - Credential store access:
- Search: rg -n "keychain|keytar|credential.store|SecItemCopyMatching|CredRead|keyring" {CLONE_DIR}

PRM-05 - Scope expansion on update:
- Check if permissions/scopes are documented and versioned

PRM-06 - Human-in-the-loop:
- Check if destructive operations (delete, modify, overwrite) require user confirmation
- Search: rg -n "confirm|prompt|approve|--force|--yes|-y\b" {CLONE_DIR} --type-add 'code:*.{ts,js,py,go,rs,java,rb}' -t code

### D8: Runtime Sandboxing (weight: 7)

RUN-01 - Minimal privileges:
- Check Dockerfiles: rg -n "USER|--privileged|cap_add|cap_drop|no-new-privileges|SYS_ADMIN" {CLONE_DIR} --glob "Dockerfile*"
- Check for root execution

RUN-02 - Filesystem/process isolation:
- Check for sandbox configuration, read-only mounts

RUN-03 - Resource limits:
- Search: rg -n "timeout|deadline|WithTimeout|AbortController|ulimit|cgroup|--memory|--cpus" {CLONE_DIR}

RUN-04 - Container/sandbox config:
- Find: find {CLONE_DIR} -name "Dockerfile*" -o -name "docker-compose*" -o -name "*.seccomp.json" -o -name "sandbox*" -o -name ".devcontainer" 2>/dev/null

RUN-05 - Workspace trust model:
- Check if the plugin treats workspace content as untrusted

## Output Format

Return findings in this exact format:

SCORES:
- SEC-01: [0-5] - [one-line evidence]
- SEC-02: [0-5] - [one-line evidence]
- SEC-03: [0-5] - [one-line evidence]
- SEC-04: [0-5] - [one-line evidence]
- SEC-05: [0-5 or N/A] - [one-line evidence]
- SEC-06: [0-5 or N/A] - [one-line evidence]
- SCA-01: [0-5] - [one-line evidence]
- SCA-02: [0-5] - [one-line evidence]
- SCA-03: [0-5] - [one-line evidence]
- SCA-04: [0-5] - [one-line evidence]
- PRM-01: [0-5] - [one-line evidence]
- PRM-02: [0-5] - [one-line evidence]
- PRM-03: [0-5] - [one-line evidence]
- PRM-04: [0-5] - [one-line evidence]
- PRM-05: [0-5] - [one-line evidence]
- PRM-06: [0-5] - [one-line evidence]
- RUN-01: [0-5 or N/A] - [one-line evidence]
- RUN-02: [0-5 or N/A] - [one-line evidence]
- RUN-03: [0-5] - [one-line evidence]
- RUN-04: [0-5 or N/A] - [one-line evidence]
- RUN-05: [0-5] - [one-line evidence]

HARD-FAIL GATES:
- SEC-01 < 5? [yes/no] - [evidence]
- PRM-06 scores 0-1? [yes/no] - [evidence]
- RUN-01 scores 0-1? [yes/no] - [evidence]

SECRETS FOUND:
- [list each potential secret with file:line, or "None found"]

DANGEROUS PATTERNS:
- [list each dangerous code pattern with file:line, or "None found"]

SENSITIVE PATH ACCESS:
- [list each sensitive path reference with file:line, or "None found"]

KEY FINDINGS:
- [bullet list of most critical findings, max 5]
