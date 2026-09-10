"""Guard test: the fleet-loop safety wall must allow branch push + PR create,
and must still deny merge, force-push, base-branch push, and every other
irreversible action. Run after any change to fleet_guard.py.
"""
import json, os, subprocess, sys, tempfile
HOOK = os.path.expanduser("~/.claude/hooks/fleet_guard.py")

# The guard is active when ./.fleet/ACTIVE exists in cwd, so the suite runs
# against a throwaway dir carrying that marker.
CWD = tempfile.mkdtemp(prefix="guardtest-")
os.makedirs(os.path.join(CWD, ".fleet"), exist_ok=True)
open(os.path.join(CWD, ".fleet", "ACTIVE"), "w").close()

def run(cmd):
    p = subprocess.run([sys.executable, HOOK],
        input=json.dumps({"tool_name":"Bash","tool_input":{"command":cmd},"cwd":CWD}),
        capture_output=True, text=True)
    out = p.stdout.strip()
    if not out: return None
    return json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"].split("(")[1].split(")")[0]

ALLOW = [
 "git push -u origin feat/one-123-add-retry",
 "git push origin HEAD",
 "git push",
 "gh pr create --title 'feat: add retry' --body 'x'",
 "glab mr create --title x",
 "gh pr checks 157",
 "gh pr view 157 --json statusCheckRollup",
 "gh api repos/o/r/pulls/157/comments",
 "gh pr comment 157 --body 'addressed'",
 "yarn test && yarn typecheck",
 "git commit -m 'feat: slice'",
 "git rebase origin/main",
]
DENY = [
 "git push --force origin feat/x",
 "git push -f origin feat/x",
 "git push --force-with-lease origin feat/x",
 "git push origin main",
 "git push origin HEAD:main",
 "git push origin develop",
 "git push origin staging",
 "git push origin --delete feat/x",
 "gh pr merge 157 --squash",
 "gh pr create --title x --body y --auto",
 "glab mr merge 12",
 "gh release create v1.0.0",
 "terraform apply",
 "rm -rf ./src",
 "git reset --hard HEAD~1",
 "aws ecs update-service --cluster x",
]
fails = 0
for c in ALLOW:
    lbl = run(c)
    if lbl is not None:
        print(f"FAIL should-allow but DENIED({lbl}): {c}"); fails += 1
for c in DENY:
    lbl = run(c)
    if lbl is None:
        print(f"FAIL should-deny but ALLOWED: {c}"); fails += 1
print(f"\n{len(ALLOW)} allow + {len(DENY)} deny cases, {fails} failure(s)")
sys.exit(1 if fails else 0)
