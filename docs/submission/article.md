# Teaching an on-call agent to remember: building IncidentIQ

> Template: each team member should publish their own version. Rewrite the
> "My part" section in your own words and use your own name.

At 3 a.m. a pager goes off: checkout is failing and database connections are
timing out. Someone on the team fixed this exact problem four months ago, but
they're asleep, the postmortem is buried in a wiki, and the on-call engineer
starts from zero.

Most AI incident assistants have the same problem. They read the alert in
front of them and give sensible, generic advice, because they have no memory
of what actually happened last time.

## The idea

IncidentIQ is an incident responder that learns from resolved incidents. Two
rules shape it:

1. **Recall before reasoning.** Before the model sees a new incident, we ask
   Hindsight, a persistent memory system, for similar past experiences. We
   match on the service, symptoms, logs, and deploy version.
2. **Retain only confirmed outcomes.** Memory is written only after an engineer
   resolves an incident: the real root cause, the fix, whether it worked, how
   long it took, and the lessons learned. Failed fixes are stored too, because
   "we tried restarting and it didn't help" is valuable to remember.

## Architecture

A FastAPI backend stores incidents in SQLite, calls Hindsight's recall and
retain APIs, and sends the incident plus recalled memories to an LLM with a
strict JSON schema. The output is validated with Pydantic: root cause,
confidence, evidence, recommended actions, similar incidents, and the
uncertainties it still has. A React dashboard makes the memory visible:
every answer shows the memories behind it, with match scores and dates.

## Showing the difference

The feature I'm proudest of is the before/after view. The same incident is
analyzed twice, once with recall switched off and once with it on. Without
memory, the agent suggests "check the database and consider scaling." With
memory, it points to a connection-pool leak introduced by a deploy, cites the
two past incidents where that happened, and recommends the rollback plus
pool-size fix that resolved them in under 20 minutes.

## What we learned

- Showing the recalled memories matters as much as the answer. Engineers trust
  a recommendation when they can see which incident it came from.
- Recording failed fixes improved suggestions more than we expected.
- Structured output with validation turned a chatty model into something a
  dashboard can render reliably.

## My part

_(Describe what you personally built or learned.)_

## Try it

Live demo: https://incident-response-agent-puce.vercel.app/
Code: https://github.com/astacatalyst/Incident-Response-Agent
