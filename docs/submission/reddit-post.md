# Reddit share
Suggested subreddits: r/sre, r/devops, r/SideProject. Check each subreddit's self-promotion rules first.

**Title:** I built an incident-response agent that remembers how past outages were fixed. Here's the same incident answered with and without memory.

**Body:**
Most AI tools for on-call read the current alert and give generic advice. We wanted one that learns from the team's own history.

How it works:
- Before analyzing a new incident, it recalls similar resolved incidents from a persistent memory store (Hindsight)
- The LLM gets only the memories that were actually recalled, and returns structured output: root cause, confidence, evidence, and actions
- When an engineer resolves an incident, the confirmed root cause, fix, outcome (including failed fixes) and lessons are saved back to memory

There's a before/after screen that runs the same incident both ways, so you can see what memory changes.

Demo: https://incident-response-agent-puce.vercel.app/
Code (FastAPI + React): https://github.com/astacatalyst/Incident-Response-Agent

I'd love feedback from people who carry a pager. What would you want it to remember?
