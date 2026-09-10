# 0002: This repo is personal dev skills, not work runbooks

## Status

Accepted, 2026-09-10.

## Context

The obvious first pass at this repo swept in every skill on the machine, which meant production access runbooks and customer investigation flows sat next to general development skills. The scan before the first push found two AWS account IDs across four files in a public repo.

Account IDs are not credentials, and the fix could have been to scrub them. But the scan surfaced the real question: what is this repo actually for. The answer is personal dev skills, the habits worth making repeatable across any codebase, not the runbooks for one employer's infrastructure.

## Decision

Employer-specific ops skills stay out. They live in `~/.claude/skills` locally, where they are useful and not published.

Repo-specific skills also stay out. They live in their own repo's `.claude/skills/`, where they load automatically and cannot drift from the code they describe.

What is left is the general layer, and `AGENTS.md` states the three tests a candidate has to pass.

## Consequences

The repo starts small, with two shipped skills, which is honest about how many skills are actually general. Empty buckets for `workflow/` and `review/` name the gaps rather than hiding them.

Skills that are close but too coupled go to `in-progress/` with a note on exactly what would have to be generalized, so promotion is a known piece of work rather than a judgement call made again later.
