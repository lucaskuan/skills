# fleet-loop

## What it does

Runs one repo as an autonomous worker. Reads the repo's objective from the tracker, does one verifiable reversible slice per cycle, hard-stops at anything irreversible, checkpoints, and writes STATUS for the manager to read.

Configuration lives in the repo at `.fleet/FLEET.md`: the verify command, the tracker wiring, the budget, and the patterns that count as irreversible.

## When to reach for it

You want a repo to make progress toward a known objective while you are away, and you want to trust what you find when you come back. Run it from inside the repo.

## Common questions

**Why one slice per cycle?** A slice that is verifiable and reversible can be judged on its own. A large batch cannot, which is exactly how agent output turns into review debt.

**Run it in the repo, or as a subagent?** In the repo. A subagent spawned from a parent directory inherits the parent's conventions file, not the target repo's, so it works competently without knowing the rules it is supposed to follow. The failure is silent, which is what makes it worth stating.

**What counts as irreversible?** Whatever the repo's `.fleet/FLEET.md` names: migrations, pushes, anything touching a shared environment. The loop stops and surfaces it. It does not ask twice and it does not decide.

**It stopped and I do not know why.** STATUS carries the reason. A loop that stops with a written reason is working correctly; a loop that stops silently is the failure case.

## It's working if

Every cycle leaves three things: a STATUS entry, a checkpoint, and a change you could revert with one command. A cycle that produced no verifiable artifact should have stopped instead of continuing.
