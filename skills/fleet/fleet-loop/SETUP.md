# Fleet setup

## 1. Protect the base branch (do this first)

A loop pushes branches and opens PRs on its own. The thing that must not happen
is a merge, and the place to prevent it is the remote, not the loop.

Enable branch protection on the base branch requiring a pull request. It is
enforced server-side, applies to every tool and every teammate rather than only
to this loop, and does not depend on which harness is running or whether a local
config is installed.

```bash
cat > /tmp/protection.json <<'JSON'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null
}
JSON

gh api -X PUT repos/<owner>/<repo>/branches/main/protection --input /tmp/protection.json
```

`enforce_admins: true` is the part that matters and it is easy to get wrong.
With it false, GitHub prints a rejection message and **lets the push through
anyway** for anyone with admin on the repo, which on your own repos is you. The
push output says both "Changes must be made through a pull request" and reports
success on the same line. Verified: with `enforce_admins: false` a direct push
to a protected main landed; with it true the same push was rejected and did not
land.

The JSON file form is deliberate. `gh api -f` sends every value as a string, and
this endpoint rejects `"0"` where it wants `0` and `"false"` where it wants
`false`.

Add required status checks later, once the checks you would gate on are actually
passing on the base branch. Requiring a check that is already red blocks every
merge, including the one that would fix it.

Confirm it took, and confirm a direct push is genuinely refused:

```bash
gh api repos/<owner>/<repo>/branches/main/protection \
  --jq '{admins: .enforce_admins.enabled, pr: .required_pull_request_reviews.required_approving_review_count}'
# -> {"admins":true,"pr":0}
```

A rejected push prints `! [remote rejected] main -> main (protected branch hook
declined)` and the remote SHA does not move. Anything else means it is not on.

Note: branch protection needs a public repo or a paid plan. On a free account a
private repo returns 403 and this layer is unavailable, which makes the local
hook below the only mechanical control you have.

Without this, a loop running unattended is trusting its own instructions not to
merge. Know that before leaving one running.

## 1b. Optional: a local backstop hook

A `PreToolUse` hook can deny irreversible commands before they execute, which
catches things branch protection does not: a local deploy, an infrastructure
apply, an outbound send. It is a second layer for unattended runs on your own
machine, not a replacement for protecting the remote.

If you want one, it registers in `~/.claude/settings.json`, which is per-machine
and not synced, so it is a per-machine step.

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

- **The merge gate (branch protection, server-side):** the base branch requires a PR, so nothing lands without one. Enforced by the remote, so it holds regardless of which tool or which person is acting.
- **Everything else irreversible (the skill's hard rules):** no force-push, no base-branch push, no deploys, no prod writes, no outbound sends. These are instructions, and a local PreToolUse hook can back them mechanically for unattended runs.
- **Verifiability (FLEET.md, per-repo):** `generation: free` only where `verify` is trustworthy; else `executor-only`.
- **Operational (loop skill):** checkpoint per slice, heartbeat, stuck-detector (3 fails), budget ceiling.
