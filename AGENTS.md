# lucaskuan/skills — instructions for AI agents

This file is the source of truth for this repo's conventions. `CLAUDE.md` points here.

## What belongs in this repo

A skill earns a place when the same thing has been explained to an agent twice. Before adding one, check it against all three:

- **It is not tied to one employer's infrastructure.** Account IDs, internal hostnames, production access runbooks, and customer-specific investigation flows stay out. This repo is public.
- **It is not tied to one codebase.** A skill that only works inside one repo belongs in that repo's `.claude/skills/`, where it loads automatically and cannot drift from the code it describes.
- **It survives losing its context.** If the skill stops making sense once you remove the names of specific people, teams, and systems, it is a runbook, not a skill.

The third test is the one that catches most candidates. Generalize by replacing the specifics with the role they play: a name becomes "the user", a tracker becomes "the tracker", a repo becomes an example in a config block.

## Bucket layout

Skills live in bucket folders under `skills/`:

- `fleet/`: autonomous agent orchestration.
- `workflow/`: daily process not tied to one repo.
- `review/`: review habits worth making repeatable.
- `in-progress/`: works for me, not ready to hand to anyone else. Public on purpose, shipped in nothing.
- `deprecated/`: no longer used, kept for history.

`fleet/`, `workflow/`, and `review/` are the **promoted** buckets. The plugin ships exactly the promoted set.

## What every promoted skill must have

1. An entry in `.claude-plugin/plugin.json`'s `skills` array.
2. A row in the top-level `README.md`, with the skill name linked to its `SKILL.md`.
3. A docs page at `docs/<bucket>/<skill-name>.md`, following [.agents/writing-docs.md](./.agents/writing-docs.md).

Skills in `in-progress/` and `deprecated/` must appear in **none** of the three. `scripts/check-manifest.sh` enforces this.

## SKILL.md frontmatter

Required:

```yaml
---
name: <kebab-case, matches the folder name>
description: <what it does, then the trigger phrases that should fire it>
---
```

The `description` is the only thing the model sees when deciding whether to load a skill, so it carries the whole routing burden. Write it as one sentence on what the skill does, then the literal phrases a user would say. A description that only names the domain will not fire.

Optional: `allowed-tools` to restrict the tool surface, `version` for skills with a changelog.

## Working on a skill

A skill is prose an agent has to follow under pressure, so the failure mode is ambiguity, not verbosity. Prefer an explicit rule over a principle. Where a skill says "never", say what to do instead.

Every skill that acts on the user's behalf states who owns the irreversible decisions, and the answer is always the human. A skill may never treat its own presence as authorization.

## Installing locally

`scripts/link-skills.sh` symlinks every non-deprecated skill into `~/.claude/skills`. Symlinks mean a `git pull` updates every installed skill. Re-run after adding, renaming, or removing a skill.

`scripts/list-skills.sh` prints every `SKILL.md` path.

`scripts/check-manifest.sh` verifies the manifest, README, and docs pages agree with what is on disk.

## Validating

After touching either manifest:

```
claude plugin validate . --strict
```
