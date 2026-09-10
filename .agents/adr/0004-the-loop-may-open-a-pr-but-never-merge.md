# 0004: The loop may open a PR, but never merge

## Status

Accepted, 2026-09-10.

## Context

The original fleet-loop was reversible-only: no push, no PR, enforced by `fleet_guard.py`. That made it safe and it made it much less useful. Work stopped at a local commit, so a human had to pick up every task and carry it the rest of the way. The bottleneck the fleet was supposed to remove was still there, one step later.

Extending the loop through to a PR means the guard has to change, and the guard is the piece the whole autonomy story rests on. Loosening it casually would be the wrong trade.

## Decision

The line is revertibility, not risk.

A pushed task branch can be deleted. An open PR can be closed. Both leave the base branch exactly as it was, and the PR is precisely the artifact a human reviews, so producing one is the loop doing its job rather than exceeding it.

A merge cannot be undone the same way. It lands code, triggers deploys, and on a shared base it is immediately other people's problem. It stays blocked.

Blocked alongside it: force-push and push to a base branch, both of which rewrite or land code without review; branch deletion; `--auto` merge flags, which are a merge wearing a PR's clothes; and releases.

CI monitoring and review-comment reading are pure reads and need no exception.

## Consequences

The loop now finishes tasks in the state a human actually wants them: a green PR with its proof in the description. The human's job shrinks to the merge decision, which is the one that needed judgement anyway.

The guard's blast radius grew, so it now has a test suite: 12 commands that must be allowed and 16 that must be denied, run after any change to the hook. A safety wall with no test is a claim, not a wall.

The residual risk is a loop opening bad PRs rather than landing bad code. That is noise, not damage, and closing a PR costs a click.
