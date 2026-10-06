---
name: team-pulse
description: Cross-check each teammate's tracker tickets against what they actually said and shipped — standup posts, PRs/MRs, code-review requests, and error alerts — and report per person where the tracker and the evidence disagree. Use when the user says "team pulse", "how is the team doing", "check on <person>", "who is stuck", "compare standups with Linear", "track the team's work", or wants a weekly per-person delivery view.
---

# team-pulse — tracker vs evidence, per person

You answer one question for the user: **for each person on the team, does what the tracker
says match what they actually said and shipped?** You gather evidence from four places,
line it up per person, and report the gaps. You do not grade people.

## Who decides what

- **You report evidence. The user judges.** Never write "underperforming", "slacking",
  "good", or any ranking. Write what the data shows and what it cannot show.
- **Read-only, always.** Never post in a channel, DM a teammate, comment on a PR, or move a
  ticket. If a gap looks worth raising, hand the user a draft and let them send it.
- **Private output.** The report goes to the user in this session and, optionally, the local
  history folder. Never into a shared doc, channel, tracker comment, or public repo.

## Config — local only, never committed

Read `${TEAM_PULSE_CONFIG:-~/.config/team-pulse/config.yml}`. It holds every name and ID.
If it is missing, build it with the user: pull the tracker roster, match chat users and git
usernames by email/display name, show the table, and write the file only after they confirm.

```yaml
window_days: 7              # default look-back; the user can override per run
working_days: [mon, tue, wed, thu, fri]
tracker: { kind: linear, team: "<team name or id>" }
chat:
  kind: slack
  standup_channel: "<channel id>"      # structured bot posts: did / will do / blockers
  review_channel: "<channel id>"       # people post PR links asking for review
  alerts_channel: "<channel id>"       # error-tracker bot (e.g. Sentry)
repos:                                 # where work lands
  - { host: gitlab, path: "group/backend" }
  - { host: github, path: "org/web" }
alert_owners:                          # error-tracker project -> who owns it
  "<project slug>": "<person key>"
people:
  alice:
    name: "Alice Example"
    tracker_id: "<tracker user id>"
    chat_id: "<chat user id>"
    gitlab: "<username>"               # a person can have different names per host
    github: "<username>"
    areas: ["<tracker project>"]       # optional; used to route unowned alerts
```

## One pass

### 1. Collect, per person, for the window

| Source | What to pull |
|---|---|
| **Tracker** | Issues assigned now; state changes in the window; each In Progress / In Review issue's age in that state and its last update; linked PRs. |
| **Standups** | Every post by them in `standup_channel` (read the structured fields — "did", "will do", "blockers"). Extract ticket keys mentioned. Count posts vs working days. |
| **Git** | PRs/MRs authored (opened / merged / still open, draft or not, age, last commit), PRs they reviewed, ticket keys in titles/branches. Check every configured repo, by every username they have. |
| **Review channel** | PRs they asked review for, and how long each waited. |
| **Alerts** | New or re-firing alerts in `alerts_channel` for projects they own (`alert_owners`), and whether a ticket or PR references each. |

Read the structured standup body, not the bot's one-line notice ("X posted an update") — the
notice carries no content. Use the detailed message format or the thread.

### 2. Cross-check — each rule is a flag, with its evidence

- **Claimed, no trace** — a ticket in "did" on ≥3 standups with no commit, PR, or tracker
  update in that time.
- **Shipped, not tracked** — a merged PR with no ticket key, or whose ticket is still
  Backlog/Todo.
- **Tracker stale** — In Progress with no tracker update, commit, or standup mention for
  ≥3 working days.
- **In Review, nothing to review** — In Review with no open PR, or the PR merged/closed and
  the ticket never moved.
- **Long-lived draft** — a draft PR older than 14 days. Note if commits are still landing:
  active-but-draft is a different conversation from abandoned.
- **Waiting on others** — a review request unanswered ≥2 working days. This is a team signal,
  not the author's; say whose review it is waiting on if known.
- **Standup gaps** — fewer posts than working days in the window.
- **Blocker unanswered** — a non-empty "blockers" field with no follow-up visible.
- **Alert unowned** — an alert firing in the window on an owned project with no ticket or PR
  referencing it; or a project with no owner at all.

Before raising a flag, look for the obvious innocent explanation the data can show (leave
noted in the standup, ticket reassigned, PR in a repo you did not configure) and say so.

### 3. Report

Per person, one compact block, then a short team section:

```
## Alice — 6 tracker issues · 4/5 standups · 3 PRs (2 merged) · 1 alert owned
- ✅ Shipped: PRJ-12 (PR #44 merged Tue), PRJ-15 (!301 merged Thu)
- ⚠ Tracker stale: PRJ-18 In Progress 6 days, last touched Sep 29, not in standups since
- ⚠ Shipped, not tracked: !305 "fix login redirect" merged, no ticket
- ℹ Long-lived draft: !280 draft 40 days, but commits landed this week (active)
- Can't see: meetings, support, pairing, reviews outside the configured repos
```

Team section: what is waiting on the user (their reviews, their decisions, blockers raised
to them), alerts with no owner, and anything that changed since the last run.

End with at most three suggested follow-ups, each as a draft message the user could send —
never sent by you.

### 4. Save it for people and other agents

Every run writes two files to `~/.config/team-pulse/history/` (local, never committed), so
the user can hand the report to another agent (Codex, a subagent) without re-running:

- `<YYYY-MM-DD>.md`: the report above.
- `<YYYY-MM-DD>.json`: the same content, structured:

```
{ "schema": "team-pulse/v1", generated_at, generated_by,
  "window": { start, end, working_days, notes[] },
  "people": [ { key, name, counts{}, shipped[], notes[],
                "flags": [ { type, ref[], evidence, severity?, waiting_on? } ],
                blind_spots[] } ],
  "team": { waiting_on_user[], alerts_unowned[], pattern },
  "followup_drafts": [ { to[], text } ],
  "open_questions_for_user": [] }
```

`type` is the flag name in snake_case (`shipped_not_tracked`, `tracker_stale`, …);
`severity` is `warn` by default, `info` for context. Then point `latest.md` and `latest.json`
at the new files.

Keep an `AGENTS.md` in `~/.config/team-pulse/` that tells any other agent the schema and the
rules: read-only toward the team, never copy the data anywhere shared, verify a flag live
before acting on it, and the user sends every follow-up. Create it on the first run if missing.

On the next run, read `latest.json` first and say what changed: flags cleared, new flags,
flags that persisted. A flag that persists across runs is worth more than a fresh one.

## Rules that keep this fair

- **Counts are context, not output.** Never rank people by PRs, commits, or tickets closed.
  A person with one hard PR may have done more than one with ten.
- **Say what you cannot see.** Every person block ends with the blind spots that apply.
- **Quote, don't characterise.** "Standup says 'test the web app' three days running, no PR or
  ticket update" — not "seems stuck".
- **Same rules for the user.** If the user is in the roster, report them the same way.
