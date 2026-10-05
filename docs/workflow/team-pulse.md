# team-pulse

## What it does

Lines up, per teammate, what the issue tracker says they are working on against the evidence of what they said and shipped: daily standup posts in chat, PRs/MRs across the configured repos, review requests, and error alerts for the projects they own. It reports where the two disagree, with the evidence for each gap, and drafts follow-ups for the user to send.

All names and IDs live in a local config file, never in the skill.

## When to reach for it

You lead a small team, the tracker is supposed to be the source of truth, and you suspect it has drifted: tickets sitting In Progress for a week, PRs merged with no ticket, standups that repeat the same line, alerts nobody picked up. Run it weekly, or before a 1:1.

It is not a performance review. It shows where the tracker and the evidence disagree; it does not say why, and it never ranks people.

## Common questions

**Why does it not just count PRs and closed tickets?** Counts reward splitting work and punish the hard ticket. They appear only as context, never as the output.

**The standup channel only shows "X posted an update".** That is the bot's notice. The content is in the structured message body; read the detailed message format or the thread, not the one-line summary.

**Someone uses different usernames on GitLab and GitHub.** Each person in the config lists every username per host. A person missing a username looks like they shipped nothing — check the roster before reading the report.

**Will it message the team?** No. It is read-only everywhere. Follow-ups come back as drafts for the user to send.

**Where do the names go?** `~/.config/team-pulse/config.yml`, outside any repo. The skill bootstraps it from the tracker roster and asks the user to confirm before writing it.

## It's working if

Every flag carries the evidence that raised it (ticket, PR, standup quote, date), and you can check any one of them in under a minute. Each person block lists what the data cannot see. Running it twice a week apart tells you which flags cleared and which persisted, and a persisting flag is the one you act on.
