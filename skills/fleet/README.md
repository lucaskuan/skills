# fleet

Autonomous agent orchestration. The manager coordinates, the loop works.

The two are deliberately asymmetric. The manager holds no repo context and never touches a live session, so it can judge work by proof rather than by reading it. The loop holds all the repo context and never makes an irreversible call. Neither one can do the other's job, which is the point.

| Skill | What it does |
|---|---|
| [`fleet-manager`](./fleet-manager/SKILL.md) | The command center. Reads STATUS and the tracker across every worker, surfaces only decisions. |
| [`fleet-loop`](./fleet-loop/SKILL.md) | Runs one repo as a worker. One reversible slice per cycle, hard-stop at irreversible actions. |
