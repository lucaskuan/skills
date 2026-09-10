#!/usr/bin/env python3
"""fleet_guard.py — PreToolUse hook: block irreversible actions during autonomous fleet loops.

This is the LOAD-BEARING safety piece of the agent-fleet system.
See the fleet-loop skill, and tests/guard_test.py for the wall it asserts.

It is a hook, NOT a skill, on purpose: skills are advisory (the model may talk
itself past them); a hook mechanically DENIES the tool call. The entire autonomy
story rests on irreversible actions being impossible, not merely discouraged.

WHAT IT DOES
  When fleet-mode is active, deny any tool call that performs an IRREVERSIBLE
  action — merge, force-push, push to a base branch, deploy, send
  (slack/email/customer), prod write, money — and tell the agent to surface it
  as a DECISION instead of doing it.

  Pushing a TASK BRANCH and opening a PR are ALLOWED: both are revertible, and
  the PR is the artifact a human reviews. Merging it is not.

  When fleet-mode is NOT active, it's a no-op (exit 0) so it never gets in the
  way of normal interactive work.

FLEET MODE
  Active when EITHER:
    - env FLEET_MODE=1 is set in the session, OR
    - a file ./.fleet/ACTIVE exists in the repo cwd (the /fleet-loop skill
      creates this while looping and removes it when it stops).

  Per-repo extra rules: if ./.fleet/FLEET.md declares extra irreversible
  patterns, they are added on top of the universal list.

CONTRACT (Claude Code PreToolUse hook)
  stdin: JSON {tool_name, tool_input, cwd, ...}
  To DENY: print a JSON object with permissionDecision=deny + reason, exit 0.
  To ALLOW/defer: exit 0 with no output.
  (Using the documented hookSpecificOutput shape; falls back to exit-2-blocks
  if the host only supports the simple protocol.)
"""
import json
import os
import re
import sys

# --- universal irreversible patterns (repo-agnostic) -------------------------
# Each entry: (label, applies_to_tool(name)->bool, matches(tool_input)->bool)

BASH_TOOLS = {"Bash"}


def _bash_cmd(tool_input):
    return (tool_input or {}).get("command", "") or ""


# Bash command patterns that are irreversible / externally-visible.
# NOTE on push/PR: a loop may push a TASK BRANCH and open a PR. Both are
# revertible (delete the branch, close the PR) and a PR is precisely the
# artifact a human reviews. What stays blocked is everything that lands or
# rewrites code without a human: merge, force-push, and pushing to a base
# branch directly. See fleet-loop's ship.md.
IRREVERSIBLE_BASH = [
    ("git-force-push",      r"\bgit\s+push\b[^|;&]*(--force(-with-lease)?\b|\s-f\b)"),
    ("git push to base",    r"\bgit\s+push\b[^|;&]*\s(origin|upstream)\s+(HEAD:)?(main|master|develop|staging|production|prod)\b"),
    ("git push --delete",   r"\bgit\s+push\b[^|;&]*(--delete\b|\s-d\b)"),
    ("gh pr merge",         r"\bgh\s+pr\s+merge\b"),
    ("glab mr merge",       r"\bglab\s+mr\s+merge\b"),
    ("gh pr create --auto", r"\bgh\s+pr\s+(create|merge)\b[^|;&]*--auto\b"),
    ("gh release",          r"\bgh\s+release\s+(create|delete|upload)\b"),
    ("deploy",              r"\b(deploy|codebuild|start-build|ecs\s+update-service|serverless\s+deploy|sls\s+deploy|kubectl\s+apply|helm\s+(install|upgrade)|terraform\s+apply|cdk\s+deploy|eb\s+deploy)\b"),
    ("aws-mutate",          r"\baws\s+\S+\s+(create|delete|put|update|start|stop|terminate|modify|run-instances|send-|invoke)\b"),
    ("npm/yarn publish",    r"\b(npm|yarn|pnpm)\s+publish\b"),
    ("docker push",         r"\bdocker\s+push\b"),
    ("prod-marker",         r"(?i)\bprod(uction)?\b.*\b(deploy|migrate|apply|write|update)\b"),
    ("curl/wget POST-ish",  r"\bcurl\b.*(-X\s*(POST|PUT|PATCH|DELETE)|--data|-d\s)"),  # external mutating request
    ("rm -rf",              r"\brm\s+-rf?\b"),                 # destructive, not git-recoverable
    ("git reset --hard",    r"\bgit\s+reset\s+--hard\b"),
    ("git clean -fdx",      r"\bgit\s+clean\b.*-\S*f"),
]

# Non-Bash tools that are inherently a "send" / external mutation.
# Match by tool name substring (covers MCP tools like slack_send_message,
# create_draft, save_issue-as-send, etc.). Reads are allowed; writes/sends denied.
IRREVERSIBLE_TOOL_NAME = [
    ("slack send",    re.compile(r"slack.*(send|post|schedule)_message|send_message.*slack", re.I)),
    ("email send",    re.compile(r"(gmail|email).*(send|create_draft)|send.*mail", re.I)),
    ("calendar send", re.compile(r"calendar.*(create|update|delete|respond)_event", re.I)),
    # NOTE: Linear/GitHub issue writes are how loops REPORT — those are allowed.
    #       We only block outbound human-facing sends + infra mutations here.
]


def fleet_active(cwd):
    if os.environ.get("FLEET_MODE") == "1":
        return True
    if cwd and os.path.exists(os.path.join(cwd, ".fleet", "ACTIVE")):
        return True
    return False


def extra_patterns(cwd):
    """Read repo-specific irreversible regexes from ./.fleet/FLEET.md.

    Looks for lines under an 'irreversible:' block, one regex per '- ' item.
    Silently returns [] if absent/malformed (universal list still applies).
    """
    pats = []
    try:
        p = os.path.join(cwd, ".fleet", "FLEET.md")
        if not os.path.exists(p):
            return pats
        in_block = False
        for line in open(p, errors="ignore"):
            s = line.strip()
            if s.lower().startswith("irreversible:"):
                in_block = True
                continue
            if in_block:
                if s.startswith("- "):
                    pats.append(("repo:" + s[2:].strip(), s[2:].strip()))
                elif s and not s.startswith("#"):
                    in_block = False
    except Exception:
        pass
    return pats


def find_violation(tool_name, tool_input, cwd):
    # Bash command inspection
    if tool_name in BASH_TOOLS:
        cmd = _bash_cmd(tool_input)
        for label, pat in IRREVERSIBLE_BASH + extra_patterns(cwd):
            try:
                if re.search(pat, cmd):
                    return label, cmd
            except re.error:
                continue
    # Tool-name inspection (MCP sends etc.)
    for label, rx in IRREVERSIBLE_TOOL_NAME:
        if rx.search(tool_name or ""):
            return label, tool_name
    return None, None


def deny(label, detail):
    reason = (
        f"[fleet_guard] BLOCKED irreversible action ({label}): {detail}\n"
        "Fleet mode is active — this action is a DECISION, not autonomous work.\n"
        "Do NOT retry. Instead: record it as a decision on this loop's tracker issue "
        "(and STATUS.json status=blocked), then continue with other reversible slices "
        "or stop and wait. The human handles irreversible actions."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(out))
    # exit 0: decision conveyed via JSON. (If host uses exit-code protocol,
    # exit 2 also blocks — but 0+JSON is the documented path.)
    sys.exit(0)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # can't parse -> don't interfere
    cwd = data.get("cwd") or os.getcwd()
    if not fleet_active(cwd):
        sys.exit(0)  # no-op outside fleet mode
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    label, detail = find_violation(tool_name, tool_input, cwd)
    if label:
        deny(label, detail)
    sys.exit(0)


if __name__ == "__main__":
    main()
