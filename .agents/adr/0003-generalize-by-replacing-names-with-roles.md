# 0003: Generalize by replacing names with roles

## Status

Accepted, 2026-09-10.

## Context

The fleet skills were written for one person and one setup. They referred to the user by name, hardcoded one issue tracker, and used one repo as the example config. That reads fine when one person uses them and badly when they are published.

The tempting move was to leave them alone, on the grounds that they work. The cost of that is a skill nobody else can read, which stops it from being a skill and makes it a personal note.

## Decision

Generalize by replacing each specific with the role it plays. A name becomes "the user". A marker like `NEEDS-LUCAS:` becomes `NEEDS-HUMAN:`. A tracker stays named where the integration is real, since pretending it is generic would make the instructions unfollowable, but the surrounding prose says "the tracker".

The line is: replace what is incidental, keep what is load-bearing. An example config block naming a real repo is fine, because a reader needs to see a filled-in example to write their own.

## Consequences

A skill that survives this treatment was general all along. A skill that stops making sense afterwards was a runbook, and `AGENTS.md` now uses exactly that as the third admission test.
