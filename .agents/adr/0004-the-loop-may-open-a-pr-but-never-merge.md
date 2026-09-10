# 0004: The loop may open a PR, but never merge, and the remote enforces it

## Status

Accepted, 2026-09-10.

## Context

The original fleet-loop was reversible-only: no push, no PR. That made it safe and much less useful. Work stopped at a local commit, so a human picked up every task and carried it the rest of the way. The bottleneck the fleet was meant to remove was still there, one step later.

Extending the loop through to a PR raises the obvious question of what stops it going one step further and merging.

## Decision

**The line is revertibility.** A pushed task branch can be deleted, an open PR can be closed, and both leave the base branch as it was. A merge lands code, may trigger a deploy, and on a shared base is immediately other people's problem. So the loop pushes and opens PRs, and never merges.

**The enforcement lives on the remote, not in the loop.** Branch protection requiring a pull request is the mechanism. It is enforced server-side, applies to every tool and every teammate rather than only to this loop, and survives a machine that is missing a local config.

A local `PreToolUse` hook was the first implementation and is now optional. It remains a useful second layer, because it catches what branch protection cannot: a local deploy, an infrastructure apply, an outbound send. Shipping it as the *primary* control was the mistake, since it put a safety claim in a file that has to be installed separately on every machine to be true.

Two limits of the remote control are worth recording, both found by testing rather than by reading the docs:

- **`enforce_admins` must be true.** With it false, GitHub prints "Changes must be made through a pull request" and lets the push land anyway for anyone with admin. On a personal repo that is the owner, so the default reads as protection while providing none.
- **Private repos on free accounts cannot use it at all**, returning 403. Where that applies, the local hook is the only mechanical control available, which is a reason to keep it maintained rather than delete it.

## Consequences

The loop finishes tasks in the state a human wants: a green PR with its proof in the description. The human's job shrinks to the merge decision, which needed judgement anyway.

Setup gains a required first step, and skipping it is now an explicit risk the setup doc names rather than a silent one.

The residual risk is a loop opening bad PRs rather than landing bad code. That is noise, not damage, and closing a PR costs a click.
