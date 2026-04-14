#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / "prompts"
PROMPT_FILES = [
    PROMPT_DIR / "manifest-auditor.md",
    PROMPT_DIR / "code-scanner.md",
    PROMPT_DIR / "permissions-runtime-scanner.md",
    PROMPT_DIR / "network-mcp-scanner.md",
    PROMPT_DIR / "ci-governance.md",
]
CHECKLIST = ROOT / "unified-checklist.md"
README = ROOT / "README.md"
SKILL = ROOT / "skill.md"
REPORT_TEMPLATE = PROMPT_DIR / "report-template.md"

CHECKLIST_ITEM_RE = re.compile(r"^\| ([A-Z]{3}-\d{2}) \|", re.MULTILINE)
PROMPT_ITEM_RE = re.compile(r"^([A-Z]{3}-\d{2}) - ", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\{([A-Z][A-Z0-9_]+)\}")

ALLOWED_PROMPT_PLACEHOLDERS = {
    "CLONE_DIR",
    "ECOSYSTEM",
    "OWNER",
    "REPO",
    "REPO_URL",
}

REQUIRED_FILES = [
    ROOT / "skill.md",
    ROOT / "README.md",
    ROOT / "unified-checklist.md",
    ROOT / "scripts" / "validate-skill.py",
    PROMPT_DIR / "manifest-auditor.md",
    PROMPT_DIR / "code-scanner.md",
    PROMPT_DIR / "permissions-runtime-scanner.md",
    PROMPT_DIR / "network-mcp-scanner.md",
    PROMPT_DIR / "ci-governance.md",
    PROMPT_DIR / "report-template.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_files_exist(errors: list[str]) -> None:
    for path in REQUIRED_FILES:
        if not path.exists():
            add_error(errors, f"Missing required file: {path.relative_to(ROOT)}")


def validate_checklist(errors: list[str]) -> None:
    checklist_ids = CHECKLIST_ITEM_RE.findall(read_text(CHECKLIST))
    prompt_ids: list[str] = []
    for path in PROMPT_FILES:
        prompt_ids.extend(PROMPT_ITEM_RE.findall(read_text(path)))

    if len(checklist_ids) != 76:
        add_error(errors, f"Expected 76 checklist items in unified-checklist.md, found {len(checklist_ids)}")
    if len(prompt_ids) != 76:
        add_error(errors, f"Expected 76 checklist items across prompts, found {len(prompt_ids)}")
    if len(checklist_ids) != len(set(checklist_ids)):
        add_error(errors, "Duplicate checklist IDs found in unified-checklist.md")
    if len(prompt_ids) != len(set(prompt_ids)):
        add_error(errors, "Duplicate checklist IDs found across prompt files")

    checklist_only = sorted(set(checklist_ids) - set(prompt_ids))
    prompt_only = sorted(set(prompt_ids) - set(checklist_ids))
    if checklist_only:
        add_error(errors, f"Checklist IDs missing from prompts: {', '.join(checklist_only)}")
    if prompt_only:
        add_error(errors, f"Prompt IDs missing from unified-checklist.md: {', '.join(prompt_only)}")


def validate_placeholders(errors: list[str]) -> None:
    skill_text = read_text(SKILL)
    seen_placeholders: set[str] = set()

    for path in PROMPT_FILES:
        placeholders = set(PLACEHOLDER_RE.findall(read_text(path)))
        unknown = sorted(placeholders - ALLOWED_PROMPT_PLACEHOLDERS)
        if unknown:
            add_error(errors, f"Unknown placeholders in {path.name}: {', '.join(unknown)}")
        seen_placeholders |= placeholders

    for placeholder in sorted(seen_placeholders):
        if placeholder not in skill_text:
            add_error(errors, f"skill.md does not mention placeholder {placeholder}")


def validate_docs(errors: list[str]) -> None:
    readme_text = read_text(README)
    skill_text = read_text(SKILL)
    template_text = read_text(REPORT_TEMPLATE)
    prompt_texts = {path.name: read_text(path) for path in PROMPT_FILES}

    if "76 checklist items" not in readme_text:
        add_error(errors, "README.md does not mention the canonical 76 checklist items")
    if "76 checklist items" not in skill_text:
        add_error(errors, "skill.md does not mention the canonical 76 checklist items")
    if "unified-checklist.md" not in readme_text or "unified-checklist.md" not in skill_text:
        add_error(errors, "Canonical checklist reference is missing from README.md or skill.md")
    if "review-policy.json" in readme_text or "review-policy.json" in skill_text:
        add_error(errors, "README.md or skill.md still references review-policy.json")

    d13_row = "| 13 | Dynamic Testing & Fuzzing | N/A | N/A | N/A |"
    if d13_row not in template_text:
        add_error(errors, "report-template.md does not mark D13 as fully N/A")
    if "## Risk Level: {RISK_LEVEL}" not in template_text:
        add_error(errors, "report-template.md does not expose the Risk Level placeholder")
    if "{RISK_FLAGS}" not in template_text:
        add_error(errors, "report-template.md does not expose the Risk Flags placeholder")
    if "{FULL_DEPENDENCY_LICENSE_INVENTORY}" not in template_text:
        add_error(errors, "report-template.md does not expose the full dependency/license inventory placeholder")

    required_gate_lines = {
        "manifest-auditor.md": "SUP-02 critical flag? [VERIFIED/POTENTIAL/NO] - [evidence]",
        "code-scanner.md": "SEC-01 critical flag? [VERIFIED/POTENTIAL/NO] - [evidence]",
        "network-mcp-scanner.md": "MCP-01 critical flag? [VERIFIED/POTENTIAL/NO] - [evidence]",
        "permissions-runtime-scanner.md": "PRM-06 critical flag? [VERIFIED/POTENTIAL/NO] - [evidence]",
    }
    for filename, snippet in required_gate_lines.items():
        text = prompt_texts[filename]
        if snippet not in text:
            add_error(errors, f"{filename} is missing the expected critical-flag status line")
        if "POLICY_" in text:
            add_error(errors, f"{filename} still contains POLICY_ placeholders")

    manifest_text = prompt_texts["manifest-auditor.md"]
    if "FULL DEPENDENCY AND LICENSE INVENTORY:" not in manifest_text:
        add_error(errors, "manifest-auditor.md is missing the full dependency/license inventory output block")

    for filename, text in prompt_texts.items():
        if "review-policy.json" in text:
            add_error(errors, f"{filename} still references review-policy.json")


def main() -> int:
    errors: list[str] = []
    validate_files_exist(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    validate_checklist(errors)
    validate_placeholders(errors)
    validate_docs(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: review-plugin is internally consistent")
    print(" - checklist items: 76")
    print(" - prompt files: 5")
    print(" - D13: static-review-only, N/A")
    return 0


if __name__ == "__main__":
    sys.exit(main())
