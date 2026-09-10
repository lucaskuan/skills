# skills

My personal dev skills. The habits I want an agent to repeat exactly, written down once.

The rule for what lives here: a skill earns a place when I have explained the same thing to an agent twice. Anything tied to one employer's infrastructure stays out, and anything tied to one codebase stays in that codebase's `.claude/skills/`.

## Install

As a Claude Code plugin:

```
/plugin marketplace add lucaskuan/skills
/plugin install lucaskuan-skills@lucaskuan
```

Or symlink for local development, so a `git pull` updates every installed skill:

```
git clone https://github.com/lucaskuan/skills
cd skills && ./scripts/link-skills.sh
```

## Skills

### Fleet

Running repos as autonomous workers, and keeping a human in the loop for exactly the decisions that need one.

| Skill | What it does |
|---|---|
| [`fleet-manager`](./skills/fleet/fleet-manager/SKILL.md) | The command center. Reads every worker's STATUS and tracker, judges health by proof rather than by reading the work, surfaces only decisions. Holds zero repo context on purpose. |
| [`fleet-loop`](./skills/fleet/fleet-loop/SKILL.md) | Takes a task to a green PR unsupervised. Test-first in vertical slices with the affected specs run locally at every step, then push, fix failing CI, fix review comments, and stop for a human to merge. |

### Workflow

Empty. For daily process that is not tied to one repo.

### Review

Empty. For the review habits worth making repeatable.

## In progress

[`in-progress/`](./skills/in-progress/README.md) holds skills that work for me but are not ready to hand to anyone else. They ship in nothing and are listed here only so I do not forget them.

## Conventions

[AGENTS.md](./AGENTS.md) is the source of truth: bucket layout, what a promoted skill must have, the frontmatter contract, and what disqualifies a skill from this repo.

## License

MIT
