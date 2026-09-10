# fleet

Autonomous agent orchestration. The manager coordinates, the loop works.

The two are deliberately asymmetric. The manager holds no repo context and never touches a live session, so it can judge work by proof rather than by reading it. The loop holds all the repo context and never makes the one call that cannot be undone. Neither can do the other's job, which is the point.

The loop pushes branches and opens PRs on its own, and never merges. What enforces that is branch protection on the base branch, set up before the first run: server-side, applying to every tool and every person, not dependent on a local config. See `fleet-loop/SETUP.md`, and set `enforce_admins: true` or it will not hold against you.

| Skill | What it does |
|---|---|
| [`fleet-manager`](./fleet-manager/SKILL.md) | The command center. Reads STATUS and the tracker across every worker, surfaces only decisions. |
| [`fleet-loop`](./fleet-loop/SKILL.md) | Takes a task to a green PR unsupervised: TDD slices verified locally, push, fix failing CI, fix review comments. Stops at merge. |
