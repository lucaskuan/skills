# lucaskuan/skills

Personal dev skills: the habits worth making repeatable across any codebase.

## Language

**Skill**:
A folder containing a `SKILL.md`, loadable by an agent harness. Named in kebab-case, matching its folder.

**Bucket**:
A top-level folder under `skills/` grouping skills by what they are for. `fleet`, `workflow`, `review`, `in-progress`, `deprecated`.
_Avoid_: category, group

**Promoted**:
A skill in `fleet/`, `workflow/`, or `review/`. Promoted skills ship in the plugin and carry a README row and a docs page. The set is exactly what `.claude-plugin/plugin.json` lists.

**Blackboard**:
The coordination surface between a fleet manager and its workers: each repo's `.fleet/STATUS.json` plus the issue tracker. Workers write, the manager reads. The manager never messages a running worker directly.

**Slice**:
One cycle's worth of work from a fleet worker: one seam, one failing test, the minimal code that passes it, one commit. Verifiable and reversible, or it should not have been attempted.

**Seam**:
The public boundary a test observes behavior at, without reaching inside. Named in the plan before the first test, and repeated in the PR description so a reviewer can object to the choice.

**Fix round**:
One pass of reading CI and review feedback, fixing it, and pushing. Capped, because a loop that fixes forever is stuck without knowing it.

**Proof**:
The output of a repo's `verify` command. What the manager judges a worker by, in place of reading the worker's code.

## Relationships

- A **Bucket** holds many **Skills**
- A **Promoted** skill has exactly one docs page and one `plugin.json` entry
- A fleet manager and every fleet worker communicate only through the **Blackboard**
- A manager judges a worker by **Proof**, never by reading its **Slices**

## Flagged ambiguities

- "fleet" names both the set of running workers and the bucket holding the two skills that implement it. Tolerated: context disambiguates, and inventing a second word for the same idea would cost more than it saves.
