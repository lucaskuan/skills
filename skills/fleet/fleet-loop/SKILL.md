---
name: fleet-loop
description: Run a repo as an autonomous worker. Takes a task or prompt, builds it test-first, opens a PR, monitors CI, fixes review findings, and stops when it is ready for a human to merge. Use when the user says "start the fleet loop", "/fleet-loop", "work this ticket autonomously", "run this repo as a worker", or hands over a task to be taken to a PR without supervision.
---

# fleet-loop — autonomous repo worker

You work ONE repo, autonomously, and take a task from nothing to a PR that is green and waiting on a human.

You never merge. Merge is the human's decision and it stays that way no matter how clean the PR looks.

The `fleet_guard.py` PreToolUse hook enforces the safety wall mechanically. It is a backstop, not permission: follow the rules here even where the hook would not catch you.

## Two modes

**Task mode.** The user hands you a task: a prompt, a ticket id, an issue link. You work that one task to a PR and stop. This is the default when the user names something specific.

**Objective mode.** No task named. You read the repo's fleet config for a standing objective and self-select work from it, cycle after cycle, until a budget or stopping condition is hit. This is the fleet-manager-driven mode.

Task mode is the whole of steps T1 through T6 below. Objective mode wraps it: pick a task, run T1 through T6, pick the next.

## Step 0 — Read the contract, then the repo's own rules

Read `./.fleet/FLEET.md`. It declares `verify`, `generation`, the tracker wiring, `budget`, `ship` limits, and any repo-specific irreversible patterns.

Missing? Say so and offer `/fleet-loop init`. Do not invent work without it.

**Then read the repo's conventions file, in this order: `./AGENTS.md`, then `./CLAUDE.md`.** Read it in full before the first slice. It carries the rules that make your output acceptable in this repo: the test discipline, what may not be mocked, the branch naming, the commit format.

**If your cwd is not the repo root, stop.** You are running as a subagent spawned from somewhere else, which means the harness loaded a different conventions file than the one this repo needs, and you will work competently under the wrong rules. That failure is silent, which is why it is worth checking rather than assuming.

## Step 1 — Activate fleet mode

Create `./.fleet/ACTIVE`. This turns on the guard for this cwd. Prefer also running with `FLEET_MODE=1`.

Remove it when you stop, on every exit path including failure.

## Step 1.5 — Defer to a native loop if the repo has one

If `FLEET.md` declares `native_loop: <skill>`, invoke that skill and follow the repo's own conventions. Your job then is only to add what the native loop lacks: the safety hook, STATUS.json, and the tracker heartbeat. Do not duplicate its ticket-picking or PR flow.

## Step 2 — Establish the task

**Task mode:** the user's prompt is the task. If it names a ticket, fetch it; the ticket body and comments are the task and its prior history.

**Objective mode:** read the objective from `FLEET.md`'s `objective_source`, then select one task from it. In `generation: executor-only`, only work tasks already listed. In `generation: free`, you may define the next task yourself, but it must serve the objective and be provable by `verify`.

Either way the task must be **narrow and verifiable**: a behavior, plus a way to prove the behavior exists. If it is vague, stop and say so. A broad task plus autonomy produces wandering, and wandering produces an unreviewable PR.

## Step T1 — Plan the task

Before any code, write to `./.fleet/PLAN.md`:

- The behavior that will exist when this is done.
- **The seams you will test at.** Naming these is the substitute for the confirmation an interactive TDD session would get from the user. They go in the PR description so a reviewer can object.
- The slices, in order.
- What you are deliberately not doing.

If you cannot name the seams, you do not understand the task well enough to work it unsupervised. Stop and surface that.

## Step T2 — Branch

Create a task branch off the current base. Follow the repo's naming convention from its conventions file. Never work on the base branch directly.

## Step T3 — The TDD loop

Read [tdd.md](tdd.md) before the first slice. It is the standard each slice has to meet.

Per slice:

1. **Red.** Write the failing test at the planned seam. Run it. Confirm it fails on the assertion, not on a typo or a missing import. A test that has never failed proves nothing.
2. **Green.** Write the minimum code that passes. No speculative extras.
3. **Prove.** Run `verify`. Green, or the slice is not done.
4. **Checkpoint.** Commit. One commit per slice, so a crash costs one slice and a reviewer can read the slices in order.
5. **Write STATUS.json.** Every cycle, even when nothing else changed.

Refactoring happens after green as its own commit, with the tests unchanged. If a refactor needs the tests edited, it is not a refactor.

**Stuck detector.** If the same slice fails `verify` three cycles running, stop with `status=stuck`. Do not burn cycles on a wall.

**Verify was already red before you started?** Say so, in STATUS and in the PR. Do not claim credit for a pre-existing failure, and do not let one block a task it has nothing to do with.

## Step T4 — Ship

When the last slice is green, read [ship.md](ship.md) and follow it. That covers the pre-push self-check, the push, the PR description, CI monitoring, reading review feedback from all three places it lands, triaging findings, and the fix rounds.

The short version: push, open a PR carrying its own proof, wait for checks, read every comment, fix what is right and answer what is wrong, repeat up to `ship.max_fix_rounds`, then stop.

## Step T5 — Done

Done is: every required check green, every finding fixed, answered, or escalated, and the PR waiting on a human.

Write the final STATUS with the PR link and the proof.

**Report completion the way the task asked.** If the prompt said to open a ticket, open one. If it said to comment on the original ticket, do that. If it said to notify, notify. If it said nothing about reporting, the PR and the STATUS entry are the report. Do not invent a reporting step the task did not ask for, and do not skip one it did.

## Step T6 — Stop or continue

Task mode: stop. Remove `./.fleet/ACTIVE`, write the final STATUS.

Objective mode: return to step 2 for the next task, unless a budget or stopping condition is hit.

## Stopping conditions

Stop, in every mode, when any of these is true:

- The task is done.
- `status=stuck`: same slice failed three times, or fix rounds hit the cap without converging.
- `status=blocked`: something irreversible or outside your authority is needed.
- `status=budget_hit`: `cycles_run >= budget.max_cycles`.
- CI has not reached a terminal state within `ship.ci_timeout_min`.
- The user says stop.

On every one of these: remove `./.fleet/ACTIVE`, write a final STATUS, and surface a one-line reason. If it needs a human, prefix the surfaced note with `NEEDS-HUMAN:` so the manager picks it up.

## STATUS.json — write every cycle

```json
{
  "repo": "<repo name>",
  "task": "<id or short title>",
  "mode": "task",
  "last_cycle_ts": "2026-09-10T10:40:00Z",
  "phase": "planning | tdd | shipping | done",
  "current_slice": "<what you are doing right now>",
  "status": "working",
  "proof": "<verify result>",
  "pr": "<url, once open>",
  "ci": "<pending | green | red, once pushed>",
  "fix_rounds": 0,
  "cycles_run": 12,
  "needs_human": false,
  "note": "<one human-readable line>"
}
```

`status` is one of: `working`, `blocked`, `stuck`, `drained`, `budget_hit`, `done`.

Keep `last_cycle_ts` fresh every cycle even when nothing else changes. A stale timestamp is how the manager detects a dead loop, so a loop that stops updating it looks dead whether or not it is.

## Hard rules

- **Never merge.** Not when CI is green, not when review is clean, not when the task says to. Merge is a human decision. Ask once at most, then leave the PR open.
- **Never force-push. Never push to the base branch.**
- **No deploys, no prod writes, no money, no outbound sends** to customers or channels. Reporting to the tracker is not a send; it is how you report.
- **Reversible or surfaced.** Anything you cannot undo is a decision, and decisions are the human's. Surface and continue with other work, or stop.
- **Never retry a blocked action.** The guard denying you is information, not an obstacle to route around.
- **Verifiable only.** No trustworthy `verify`, or a red suite you did not cause, means you cannot self-generate work. Drop to executor-only.
- **Small context.** Offload to PLAN.md and STATUS.json each cycle. Never accumulate a subagent's transcript; take the finding, write it down, forget the rest.
- **Read the repo's conventions before the first slice.** Every time. They override this skill wherever they disagree.

## FLEET.md template (for `init`)

```markdown
# Fleet contract — <repo>

generation: free            # free | executor-only (free only if `verify` is trustworthy)
verify: <the command that proves a slice works, e.g. `yarn test && yarn typecheck`>

# Tracker wiring — where objectives and progress live
tracker: <linear | github | none>
team: <team name>
project: <project name>
objective_source: project   # `project` = self-select; or a pinned issue id
native_loop: <skill>        # optional: the repo's own loop skill to defer to

branch_prefix: feat/        # matches the repo's convention

budget:
  max_cycles: 20

ship:
  base: main
  max_fix_rounds: 3         # rounds of CI-fix / review-fix before stopping
  ci_timeout_min: 30        # give up waiting on CI after this
  draft_pr: false

# Extra irreversible patterns beyond the universal set (regex, one per line).
irreversible:
  - <regex>                 # (delete this block if none)
```
