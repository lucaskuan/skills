# Fleet system — one-time setup per machine

The skills (`fleet-loop`, `fleet-manager`) and the hook script (`fleet_guard.py`)
**sync automatically** via `claude_sync.py` (skills sync as custom work product;
`fleet_guard.py` is in the HOOK_FILES list). But **hook registration lives in
`settings.json`, which is per-machine and NOT synced.** So on each machine, once:

## 1. Register the safety hook (REQUIRED — this is the safety wall)

Add a PreToolUse hook to `~/.claude/settings.json`:

```bash
python3 - <<'PY'
import json, os
p = os.path.expanduser("~/.claude/settings.json")
d = json.load(open(p))
pre = d.setdefault("hooks", {}).setdefault("PreToolUse", [])
if not any("fleet_guard.py" in json.dumps(h) for h in pre):
    pre.append({"matcher":"*","hooks":[{"type":"command",
        "command":"python3 ~/.claude/hooks/fleet_guard.py","timeout":10}]})
    json.dump(d, open(p,"w"), indent=4); print("registered")
else: print("already registered")
PY
chmod +x ~/.claude/hooks/fleet_guard.py
```

Verify it works:
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"gh pr merge 1"},"cwd":"/tmp"}' \
  | FLEET_MODE=1 python3 ~/.claude/hooks/fleet_guard.py
# -> prints a deny JSON. Without FLEET_MODE=1 -> no output (allowed).
```

Then run the full suite, which asserts both directions of the wall:
```bash
python3 tests/guard_test.py
# -> 12 allow + 16 deny cases, 0 failure(s)
```

Re-run it after any change to the hook. A safety wall with no test is a claim,
not a wall.

## 2. Per-repo: create a FLEET.md

In each fleet-ready repo:
```bash
/fleet-loop init      # asks for generation mode + verify command + Linear issue
```
Or copy an existing `.fleet/FLEET.md` as a template. Only give `generation: free`
to repos whose `verify` command actually proves correctness (real tests + typecheck).
Thin-tested repos → `generation: executor-only`.

A repo is fleet-ready when its verify command is trustworthy on its own. If you
would not merge on a green verify without reading the diff, the repo needs
harness work before it needs a worker.

Also gitignore the runtime files (keep FLEET.md tracked):
```
.fleet/ACTIVE
.fleet/STATUS.json
```

## 3. Run it

- Per repo: `/fleet-loop <task>` — works one task to a PR and stops.
- Per repo: `/fleet-loop` with no task — reads the standing objective from FLEET.md and self-selects work.
- Command center: `/fleet-manager` — one consolidated pass. For unattended, wrap in `/loop 20m /fleet-manager` or a `/schedule`.

## How the safety layers compose

- **Reversibility (hook, universal):** merge, force-push, base-branch push, deploy, send, prod writes and money are blocked in every fleet repo, mechanically, and cannot be talked past by the model. Pushing a task branch and opening a PR are allowed: both are revertible, and the PR is the artifact a human reviews.
- **Verifiability (FLEET.md, per-repo):** `generation: free` only where `verify` is trustworthy; else `executor-only`.
- **Operational (loop skill):** checkpoint per slice, heartbeat, stuck-detector (3 fails), budget ceiling.
