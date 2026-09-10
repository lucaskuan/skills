# fleet

Autonomous agent orchestration. The manager coordinates, the loop works.

The two are deliberately asymmetric. The manager holds no repo context and never touches a live session, so it can judge work by proof rather than by reading it. The loop holds all the repo context and never makes the one call that cannot be undone. Neither can do the other's job, which is the point.

The loop's autonomy rests on a hook, not on instructions. `fleet_guard.py` mechanically denies merge, force-push, base-branch push, deploy, and outbound sends whenever a repo has fleet mode active. Pushing a task branch and opening a PR are allowed, because both are revertible and the PR is the artifact a human reviews. A copy of the hook and its test suite ship in `fleet-loop/`.

| Skill | What it does |
|---|---|
| [`fleet-manager`](./fleet-manager/SKILL.md) | The command center. Reads STATUS and the tracker across every worker, surfaces only decisions. |
| [`fleet-loop`](./fleet-loop/SKILL.md) | Takes a task to a green PR unsupervised: TDD slices, push, CI monitoring, review fixes. Stops at merge. |
