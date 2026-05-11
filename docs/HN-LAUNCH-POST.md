# Hacker News Launch Post

**Title:** Show HN: md-knowledge-format — Markdown specs that teach humans and AI agents

**Post timing:** Tuesday–Thursday, 8–11 AM ET. Tag as `Show HN`.

---

**Body:**

Two problems, one solution.

Problem 1: Every LMS, tutorial platform, and IDE stores programming lessons in its own
proprietary format. Content creators rewrite the same material for every platform — or
accept vendor lock-in.

Problem 2: AI agents in a swarm keep repeating the same mistakes. They don't share a
brain. Fix one, and another makes the identical error hours later.

I built two tiny, complementary specs — LESSON.md and LESSONS.md — that solve both
problems with the same philosophy: Markdown + YAML front matter = actionable, portable
knowledge files.

**LESSON.md** is a universal lesson container. Write a programming tutorial once, and
any LMS, IDE, or LLM can ingest it. The spec covers title, language, difficulty, topics,
prerequisites, and objectives in YAML front matter, plus standard body sections
(Content, Exercises, Further Reading). A single CLI tool scaffolds lessons, validates
them (catches missing code block languages, empty fields, typos), and exports to
standalone HTML.

**LESSONS.md** is an agent memory file. Three sections:
- DO NOT (hard blocks — agents abort and substitute the safe alternative)
- PITFALLS (context-dependent gotchas)
- SUCCESS PATTERNS (techniques that work)

Agents read the file before every non-trivial action. When one fails, it appends a new
entry. The PR auto-merges, and within minutes every agent in the fleet learns from the
mistake. No vector DB, no embeddings, no RAG pipeline. Retrieval is literally grep.

I've been running this with my OpenClaw agent swarm for six months. Recurring mistake
classes went from ~12/month to zero of those same classes repeating. New mistakes still
happen, but each one only happens once.

The repo includes formal specs for both formats (v1.0), a single Python 3.6+ CLI (zero
mandatory dependencies), worked examples, and an LMS integration guide.

Why it works:
- It's just a file. No servers, no APIs, no databases.
- Human-auditable. Open it and see exactly why agents behave the way they do.
- Framework-agnostic. Works with any agent that can read a file.
- Keeps prompts clean. "Don't do X" rules live in the file, not in a bloated system prompt.

Repo: https://github.com/jeremymandile/md-knowledge-format

Would love feedback — especially from anyone running multi-agent systems or building
LMS tooling. What would make this more useful for your stack?

---

**First comment to post immediately after (the concrete anecdote):**

Real example of LESSONS.md working: agent "invoice-bot" generated a PDF with a € sign,
but DejaVu Sans doesn't support it — customers got a blank square in their email. Before
LESSONS.md, I'd fix the prompt and move on. Two days later, "report-gen" produced a
quarterly PDF with the same broken character — no connection made.

After LESSONS.md: invoice-bot wrote a DO NOT entry (#pdf #fonts #unicode), the PR
auto-merged, and the next time report-gen ran a PDF job, the lesson-guard plugin saw the
#pdf tag, read the entry, and switched fonts automatically. The error never appeared
again. That's the whole pitch in one paragraph.
