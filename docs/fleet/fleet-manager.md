# fleet-manager

## What it does

The command center for a fleet of autonomous repo workers. Reads every worker's STATUS file and the issue tracker, judges each worker's health by the proof it produced rather than by reading its code, writes the next objective, and surfaces only the decisions that need a human.

It holds zero repo context by design, and it never messages a running worker. Coordination goes through the blackboard: STATUS files plus tracker issues.

## When to reach for it

You have several repos running as workers and you want one consolidated view of what needs you. Reach for it to start a session, not to do repo work. If you want something fixed, the manager is the wrong tool, and that is deliberate.

## Common questions

**Why does it refuse to fix things?** Holding no repo context is what lets it judge by proof. A manager that reads the diff starts trusting the diff, which puts the review bottleneck straight back where it was.

**Why not message a running worker directly?** Coordination through the blackboard means a worker is never interrupted mid-cycle, and the state survives a session dying. A direct message is state that exists only in a transcript.

**Which decisions come to me?** Anything irreversible. The worker hard-stops, the manager surfaces it, and neither one decides.

**It says a worker is healthy but I do not believe it.** The fix is a better `verify` command in that repo's fleet config, not a manager that reads code. If the verify command does not earn trust, nothing downstream of it can.

## It's working if

You get a short list of decisions and little else. Every worker's state is accounted for, including the silent ones, because silence is the alarm. If it hands you a summary of work you now have to go read, the proof-based judgement did not happen.
