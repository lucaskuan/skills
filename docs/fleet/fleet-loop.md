# fleet-loop

## What it does

Takes one task and carries it to a pull request, unsupervised. Plans the seams it will test at, builds the behavior test-first in vertical slices, pushes a branch, opens a PR carrying its own proof, watches CI, reads review feedback, fixes what it finds, and stops when the PR is green and waiting on a human.

It does not merge. That stays a human decision no matter how clean the result looks.

Two modes. **Task mode** works one named task and stops. **Objective mode** self-selects tasks from a standing objective, cycle after cycle, which is the mode the fleet manager drives.

## When to reach for it

You have a well-specified task and you want it taken to a reviewable PR while you do something else. It works best when the repo has a `verify` command you would actually trust: if you would not merge on a green verify without reading the diff, the repo needs harness work before it needs a worker.

Run it from inside the repo.

## Common questions

**Can it merge if CI is green and review is clean?** No, and this is enforced by a hook rather than by instruction. A pushed branch and an open PR are both revertible. A merge is not, so it belongs to a human. The finished state is a PR sitting open and green.

**Why does it name the seams before writing tests?** Interactive TDD confirms seams with the user first, which an autonomous loop cannot do. Writing them into the plan and the PR description is the substitute: a reviewer who disagrees with the seam choice can say so from the PR. It also doubles as a comprehension check, since a loop that cannot name the seam does not understand the task well enough to work it alone.

**What stops it fixing CI forever?** A fix-round cap, three by default, plus an immediate stop if a round changes nothing in the failing set. Three rounds that did not converge means the task was underspecified or the failure is outside the loop's reach, and a fourth rarely finds what the first three missed.

**It says a CI failure was already broken. Is it dodging work?** It compares against the base branch's recent run before claiming that. A pre-existing failure genuinely is not the task's to fix, and both claiming credit for fixing one and being blocked by one are wrong. It surfaces it separately.

**Does it read review comments, or only CI?** Both, and comments arrive in three separate places on a GitHub PR: inline on lines, as review summaries, and as top-level comments. It reads all three and deduplicates, because bots commonly post to all three at once. Comments that land while CI is still running get folded into the current round rather than starting a new one.

**Run it in the repo, or as a subagent?** In the repo. A subagent spawned from a parent directory inherits the parent's conventions file, not the target repo's, so it works competently under the wrong rules. The loop checks its cwd at step 0 and stops rather than proceeding, because that failure is otherwise silent.

**What does it do when it finishes?** Whatever the task asked. If the prompt said to open a ticket, it opens one; if it said nothing about reporting, the PR and the STATUS entry are the report. It does not invent a reporting step, and it does not skip one that was requested.

## It's working if

The PR it opens is one you can review without asking it questions: the description states the behavior, names the seams, and carries the verify result. The commits read as one slice each, in order.

Every check is green, or the reason one is not is written down. Every review finding is fixed, answered on the thread, or escalated, with none silently ignored.

And the PR is still open. A loop that merged is a loop that broke its contract.

## Testing the safety wall

`tests/guard_test.py` asserts the wall: 12 commands that must be allowed, 16 that must be denied. Run it after any change to `fleet_guard.py`.

```
python3 skills/fleet/fleet-loop/tests/guard_test.py
```
