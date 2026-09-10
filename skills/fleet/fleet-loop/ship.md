# Ship: push, PR, CI, review

This is the phase after the last slice is green. Its job is to get a task from "green locally" to "waiting on a human to merge", and to absorb every round of automated feedback along the way without asking for help.

The whole phase is bounded. Fixing CI is real work, but a loop that fixes CI forever is a loop that is stuck and does not know it. Every wait and every fix round has a cap, stated below.

## What is allowed here

Push and PR creation are allowed. **Merge is not, and never becomes allowed.** A pushed branch and an open PR are both revertible by closing them. A merge is the irreversible step and it belongs to a human.

Also still blocked: force-push, pushing to a protected branch, deploy, and everything else in the guard's universal list.

## Step S1 — Pre-push self-check

Before pushing, run the repo's `verify` command one final time on the full branch, not just the last slice. A slice-by-slice green does not prove the branch is green.

Then read your own diff:

```
git diff <base>...HEAD --stat
git diff <base>...HEAD
```

Check three things, and fix them now rather than letting a reviewer find them:

- **Debug residue.** Stray logging, commented-out code, a `.only` on a test, a hardcoded value from local testing.
- **Scope.** Every file in the diff traceable to the task. A file you touched while exploring and left changed is scope creep, and it is the most common reason a small PR reads as a large one.
- **The generated-file ratio.** If the diff is mostly lockfiles, migration snapshots, or generated clients, say so in the PR description. A 4,000-line diff that is 3,800 lines of generated snapshot reads as unreviewable unless you tell the reviewer which 200 lines are real.

## Step S2 — Push

Push the task branch. Never `--force`, never to the base branch.

```
git push -u origin <branch>
```

If the push is rejected because the remote has moved, rebase onto the updated base, re-run `verify`, and push again. If it is rejected for any other reason, stop and surface it.

## Step S3 — Open the PR

The PR description is the only thing a reviewer reads before the diff, so it carries the proof.

```markdown
## What

<one or two sentences: the behavior that now exists>

## Why

<the task, linked>

## Seams under test

<the seams named before the first slice; a reviewer who disagrees says so here>

## Proof

<the verify command, and its result>

## Notes for review

<generated-file ratio if relevant; anything deliberately left out; any assumption made>
```

Then record the PR number in STATUS.json so the manager can see it.

## Step S4 — Monitor CI

Poll, do not guess:

```
gh pr checks <n>          # GitHub
glab ci status            # GitLab
```

Wait for every required check to reach a terminal state. Cap the total wait at `ship.ci_timeout_min` from the fleet config, default 30 minutes. On timeout, stop with `status=stuck` and surface it; a CI run that never finishes is an infrastructure problem, not a code problem, and the loop cannot fix it.

Poll on an interval matched to the run, not tightly. A suite that takes 8 minutes deserves checks every couple of minutes, not every 15 seconds.

**Review bots often appear as a check.** A check named for review is the automated reviewer, and it reaching a terminal state means its comments are ready to read. This is the signal to run step S5 even if all checks passed.

## Step S5 — Read the feedback

Review feedback arrives in three places and a loop that reads only one will miss most of it. Read all three:

```
gh api repos/<owner>/<repo>/pulls/<n>/comments    # inline, on specific lines
gh api repos/<owner>/<repo>/pulls/<n>/reviews     # review summaries + state
gh api repos/<owner>/<repo>/issues/<n>/comments   # top-level PR comments
```

The same bot commonly posts in all three at once, so deduplicate before acting.

**Comments arriving while CI is still running get handled in the same round.** Do not wait for CI to finish before reading comments that already exist. Do not start a second fix round for a comment that arrived during the first one, if the first round has not pushed yet. Fold it in.

## Step S6 — Triage and fix

For each distinct finding, decide one of three:

- **Fix it.** The finding is correct. Fix it as its own commit, TDD where it is a behavior change: a failing test that reproduces the finding, then the fix.
- **Push back.** The finding is wrong or does not apply. Reply on the thread saying why, in one or two sentences. Do not silently ignore it, and do not change correct code to satisfy an incorrect comment.
- **Escalate.** The finding is a real problem you cannot resolve inside this task's scope, or resolving it requires a decision that is not yours. Surface it and stop.

A CI failure is triaged the same way, with one addition: **check whether it was already failing before your branch.** Compare against the base branch's most recent run. A pre-existing failure is not yours to fix inside this task, and claiming credit for fixing it, or being blocked by it, are both wrong. Surface it as a separate finding and say so in the PR.

Push the fixes and return to step S4. Every push restarts CI, so every fix round is a full round.

## Step S7 — Bound the rounds

Cap fix rounds at `ship.max_fix_rounds` from the fleet config, default 3.

On hitting the cap with CI still red or findings still open, stop with `status=stuck`, and surface exactly what remains. Three rounds that did not converge means the task was underspecified or the failure is outside the loop's reach. A fourth round rarely finds what the first three did not.

**A round that fixes nothing is worse than the cap.** If a round produces no change to the failing set, stop immediately rather than spending the remaining rounds.

## Step S8 — Done

The task is done when every required check is green and every finding is fixed, answered, or escalated.

Done means **ready for a human to merge**, and nothing further. Write the final STATUS with the PR link and the proof, then report completion as the task's prompt asked. If the prompt said nothing about reporting, the STATUS entry and the PR are the report.

Never merge. Never ask to merge repeatedly. The PR sitting open and green is the finished state.
