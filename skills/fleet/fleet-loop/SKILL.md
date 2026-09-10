---
name: fleet-loop
description: Run a repo as an autonomous worker. Takes a task or prompt, builds it test-first, pushes a branch, opens a PR, fixes failing CI and review comments until they are clean, and stops with the PR waiting for a human to merge. Use when the user says "start the fleet loop", "/fleet-loop", "work this ticket autonomously", "run this repo as a worker", or hands over a task to be taken to a PR without supervision.
---

# fleet-loop — autonomous repo worker

You take ONE task in ONE repo from nothing to a pull request that is green and waiting on a human.

The full path, and none of it is optional:

1. Plan the task and name the seams you will test at.
2. Build it test-first, one slice at a time, running the affected spec after every change.
3. Run the repo's full verify before pushing.
4. Push a task branch and open a PR.
5. **Fix failing CI until it is green.**
6. **Fix review comments until they are addressed.**
7. Stop. A human merges.

**You never merge.** Not when CI is green, not when review is clean, not when the task tells you to. Closing that last step is the human's, and it is the only thing they kept.

## Two modes

**Task mode.** The user names a task: a prompt, a ticket id, an issue link. Work it to a PR and stop. Default when something specific is named.

**Objective mode.** Nothing named. Read the standing objective from the repo's fleet config, self-select a task, work it, pick the next. This is the mode the fleet manager drives.

## Step 0 — Read the contract, then the repo's own rules

Read `./.fleet/FLEET.md`: `verify`, `verify_scoped`, `generation`, tracker wiring, `budget`, `ship` limits, repo-specific irreversible patterns.

Missing? Say so and offer `/fleet-loop init`. Do not invent work without it.

**Then read the repo's conventions file in full: `./AGENTS.md`, falling back to `./CLAUDE.md`.** It carries the rules that make your output acceptable here: test discipline, what may not be mocked, branch naming, commit format. It overrides this skill wherever the two disagree.

**If your cwd is not the repo root, stop.** You are running as a subagent spawned from elsewhere, so the harness loaded a different conventions file than this repo's, and you will work competently under the wrong rules. That failure is silent, which is why it is worth checking.

## Step 1 — Activate fleet mode

Create `./.fleet/ACTIVE`. Remove it when you stop, on every exit path including failure.

## Step 1.5 — Defer to a native loop if the repo has one

If `FLEET.md` declares `native_loop: <skill>`, invoke it and follow the repo's own conventions. Your job is then only to add what it lacks: STATUS.json and the tracker heartbeat. Do not duplicate its ticket-picking or PR flow.

## Step 2 — Establish the task

**Task mode:** the prompt is the task. If it names a ticket, fetch it; body and comments are the task and its history.

**Objective mode:** read `objective_source` and select one task. Under `generation: executor-only`, only work tasks already listed. Under `generation: free`, you may define the next one, but it must serve the objective and be provable by `verify`.

The task must be **narrow and verifiable**: a behavior, plus a way to prove it exists. If it is vague, stop and say so. Broad task plus autonomy produces wandering, and wandering produces an unreviewable PR.

## Step 3 — Plan

Write `./.fleet/PLAN.md` before any code:

- The behavior that will exist when this is done.
- **The seams you will test at.** Interactive TDD confirms these with the user; you cannot, so writing them down and repeating them in the PR description is the substitute. A reviewer who disagrees can then object.
- The slices, in order.
- What you are deliberately not doing.

Cannot name the seams? You do not understand the task well enough to work it unsupervised. Stop and surface that.

## Step 4 — Branch

Create a task branch off the base, following the repo's naming convention. Never work on the base branch.

## Step 5 — The TDD loop

Read [tdd.md](tdd.md) before the first slice. It is the standard each slice has to meet.

Per slice:

1. **Red.** Write the failing test at the planned seam. Run it. Confirm it fails on the assertion, not a typo or a missing import. A test that never failed proves nothing.
2. **Green.** Write the minimum code that passes. No speculative extras.
3. **Run the affected spec.** Not the whole suite: the spec file covering what you just changed, plus anything that imports it. This is the fast feedback that catches the failure in seconds rather than in a CI round minutes later.
4. **Prove.** Run the repo's `verify`. Green, or the slice is not done.
5. **Checkpoint.** Commit. One slice, one commit, so a crash costs one slice and a reviewer reads them in order.
6. **Write STATUS.json.**

Refactoring happens after green, as its own commit, tests unchanged. If a refactor needs the tests edited, it is not a refactor.

**Stuck detector.** Same slice fails verify three cycles running, stop with `status=stuck`. Do not burn cycles on a wall.

**Verify already red before you started?** Say so in STATUS and in the PR. Do not claim credit for fixing a pre-existing failure, and do not let one block a task it has nothing to do with.

## Step 6 — Before you push

Most CI failures are avoidable locally, and every one you avoid saves a full CI round. Do all of this first.

**Run the full verify on the whole branch.** Slice-by-slice green does not prove the branch is green. Run exactly what CI runs, the command in `verify`, not a subset you believe is equivalent.

**Run every spec touching changed code.** Derive it from the diff:

```
git diff <base>...HEAD --name-only
```

For each changed source file, run its spec and the specs of files importing it. A change that passes its own test and breaks a caller's is the most common way a green local run becomes a red CI.

**Read your own diff.** Fix these now rather than letting a reviewer find them:

- **Debug residue.** Stray logging, commented-out code, a `.only` left on a test, a hardcoded local value.
- **Scope.** Every file traceable to the task. A file changed while exploring and left dirty is the most common reason a small PR reads as large.
- **Generated-file ratio.** If the diff is mostly lockfiles or migration snapshots, note it in the PR. A 4,000-line diff that is 3,800 lines of generated snapshot is unreviewable unless you say which 200 lines are real.

**Rebase onto the current base and re-run verify.** CI runs against the merge result, not your branch in isolation. A branch that is green alone and red after rebase is a failure you can find now instead of in CI.

## Step 7 — Push and open the PR

Push the task branch. **Never `--force`, never to the base branch.**

```
git push -u origin <branch>
```

Rejected because the remote moved? Rebase, re-run verify, push again. Rejected for any other reason: stop and surface it.

Then open the PR. Its description is the only thing a reviewer reads before the diff, so it carries the proof:

```markdown
## What
<the behavior that now exists, in a sentence or two>

## Why
<the task, linked>

## Seams under test
<the seams from the plan; a reviewer who disagrees says so here>

## Proof
<the verify command and its result>

## Notes for review
<generated-file ratio if relevant; anything deliberately left out; assumptions made>
```

Record the PR number in STATUS.json.

## Step 8 — Fix failing CI

Poll for the result, do not assume it:

```
gh pr checks <n>          # GitHub
glab ci status            # GitLab
```

Wait for every required check to reach a terminal state. Cap the total wait at `ship.ci_timeout_min`, default 30 minutes. On timeout stop with `status=stuck`: a run that never finishes is an infrastructure problem you cannot fix.

Poll on an interval matched to the run. An 8-minute suite deserves a check every couple of minutes, not every 15 seconds.

**A check is red. For each failure:**

1. **Read the actual log**, not the check name. `gh run view <run-id> --log-failed` gives the failing output.
2. **Reproduce it locally.** Run that exact spec on your machine. A failure you cannot reproduce locally is either environment-dependent or pre-existing, and both change what you do next.
3. **Check whether it predates your branch.** Compare against the base branch's most recent run. A pre-existing failure is not yours to fix inside this task. Say so in the PR and surface it separately. Claiming credit for fixing it and being blocked by it are both wrong.
4. **Fix it as its own commit**, test-first where it is a behavior change: a failing test reproducing it, then the fix.
5. **Re-run the affected spec locally before pushing again.** Pushing a fix you have not verified locally spends a full CI round to learn what you could have learned in seconds.

## Step 9 — Fix review comments

Feedback lands in three places on a GitHub PR, and reading one gets you a third of it:

```
gh api repos/<owner>/<repo>/pulls/<n>/comments    # inline, on lines
gh api repos/<owner>/<repo>/pulls/<n>/reviews     # review summaries and state
gh api repos/<owner>/<repo>/issues/<n>/comments   # top-level comments
```

The same bot commonly posts to all three at once. Deduplicate before acting.

**A review bot often appears as a check.** A check named for review reaching a terminal state means its comments are ready, so run this step even when every check passed.

**Comments arriving while CI is still running get handled in the same round.** Do not wait for CI to finish before reading comments that already exist, and do not open a second round for a comment that arrived during the first.

For each distinct finding, do one of three things:

- **Fix it.** The finding is right. Own commit, test-first where it changes behavior.
- **Push back.** The finding is wrong or does not apply. Reply on the thread in a sentence or two saying why. Never silently ignore one, and never change correct code to satisfy an incorrect comment.
- **Escalate.** It is a real problem outside this task's scope, or the call is not yours. Surface it and stop.

Push the fixes and return to step 8. Every push restarts CI, so every fix round is a full round.

## Step 10 — Bound the rounds

Cap fix rounds at `ship.max_fix_rounds`, default 3.

Hit the cap with CI still red or findings open: stop with `status=stuck` and surface exactly what remains. Three rounds that did not converge means the task was underspecified or the failure is out of reach, and a fourth rarely finds what the first three missed.

**A round that fixes nothing is worse than the cap.** If a round leaves the failing set unchanged, stop immediately rather than spending the rest.

## Step 11 — Done

Done is: every required check green, every finding fixed, answered, or escalated, and the PR waiting on a human.

Write the final STATUS with the PR link and the proof.

**Report the way the task asked.** Told to open a ticket, open one. Told to comment on the original, do that. Said nothing about reporting, the PR and the STATUS entry are the report. Do not invent a reporting step, and do not skip a requested one.

Task mode: stop, remove `./.fleet/ACTIVE`. Objective mode: back to step 2, unless a stopping condition is hit.

## Stopping conditions

- Task done.
- `status=stuck`: slice failed three times, or fix rounds hit the cap without converging.
- `status=blocked`: something irreversible or outside your authority is needed.
- `status=budget_hit`: `cycles_run >= budget.max_cycles`.
- CI did not reach a terminal state within `ship.ci_timeout_min`.
- The user says stop.

On any of these: remove `./.fleet/ACTIVE`, write a final STATUS, surface a one-line reason. If it needs a human, prefix the note `NEEDS-HUMAN:` so the manager picks it up.

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

`status`: `working`, `blocked`, `stuck`, `drained`, `budget_hit`, `done`.

Keep `last_cycle_ts` fresh every cycle even when nothing else changed. A stale timestamp is how the manager detects a dead loop, so a loop that stops updating it looks dead whether it is or not.

## Hard rules

- **Never merge.** Not on green CI, not on clean review, not when the task says to. Ask once at most, then leave the PR open. The PR sitting open and green is the finished state.
- **Never force-push. Never push to the base branch. Never delete a remote branch.**
- **No deploys, no prod writes, no money, no outbound sends** to customers or channels. Writing to the tracker is not a send; it is how you report.
- **Never push code you have not run locally.** Not the first push, not a CI fix, not a review fix. Every push is a full CI round, and a push made to find out whether something works is a round spent learning what a local run would have told you in seconds.
- **Reversible or surfaced.** Anything you cannot undo is a decision, and decisions are the human's. Surface it and continue with other work, or stop.
- **Verifiable only.** No trustworthy `verify`, or a red suite you did not cause, means you cannot self-generate work. Drop to executor-only.
- **Small context.** Offload to PLAN.md and STATUS.json each cycle. Never accumulate a subagent's transcript; take the finding, write it down, forget the rest.
- **Read the repo's conventions before the first slice.** Every time. They win wherever they disagree with this skill.

## Safety, and what actually enforces it

The rules above are instructions, and instructions can be rationalized past. Where the cost of that is high, put a mechanical control behind it:

- **Branch protection on the base branch** is the real wall against a bad merge. Require a PR, and require the checks that matter. It is enforced server-side, applies to every tool and every teammate, and does not depend on which harness is running.
- **A PreToolUse hook** can deny irreversible commands locally, which is useful when the loop runs unattended on your own machine. It is a local backstop, not a substitute for protection on the remote.

A loop running against an unprotected base branch is trusting its own instructions not to merge. That is worth knowing before you leave one running.

## FLEET.md template (for `init`)

```markdown
# Fleet contract — <repo>

generation: free            # free | executor-only (free only if `verify` is trustworthy)

verify: <the full gate, exactly what CI runs, e.g. `yarn test && yarn typecheck`>
verify_scoped: <how to run ONE spec, e.g. `yarn test <path>`>   # for the fast per-slice loop

# Tracker wiring
tracker: <linear | github | none>
team: <team name>
project: <project name>
objective_source: project   # `project` = self-select; or a pinned issue id
native_loop: <skill>        # optional: the repo's own loop skill to defer to

branch_prefix: feat/

budget:
  max_cycles: 20

ship:
  base: main
  max_fix_rounds: 3         # CI-fix / review-fix rounds before stopping
  ci_timeout_min: 30
  draft_pr: false

# Extra irreversible patterns beyond the universal set (regex, one per line).
irreversible:
  - <regex>                 # (delete this block if none)
```
