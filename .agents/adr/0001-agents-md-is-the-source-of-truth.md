# 0001: AGENTS.md is the source of truth, CLAUDE.md is a pointer

## Status

Accepted, 2026-09-10.

## Context

Conventions had been living in `CLAUDE.md`. Claude Code reads that file. Cursor does not: it reads `AGENTS.md` and `.cursor/rules/*.mdc`. Teammates on Cursor were therefore loading zero project conventions while believing the repo had them documented, because the file holding them was one their tool never opened.

Claude Code's `@AGENTS.md` import directive does not fix this. It works in the direction that was never the problem, and Cursor does not follow it.

## Decision

`AGENTS.md` holds the conventions. `CLAUDE.md` is a short pointer to it, plus a note that Cursor does not read `CLAUDE.md`.

A symlink was considered and rejected. Git stores symlinks correctly (mode `120000`, with the target path as the blob), so it would work mechanically. But the two files should not be identical: `CLAUDE.md` carries the cross-tool note, which is noise inside `AGENTS.md`.

## Consequences

Every tool reads the same rules. New conventions go in `AGENTS.md` by default. The ongoing cost is remembering that `CLAUDE.md` stays a pointer and never accumulates content of its own.
