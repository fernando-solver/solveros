# Philosophy — The thesis behind SolverOS

> *"The agentic part that survives is not the model. It's the editorial substrate around it."*

---

## The two things every agent needs

For an agent to perform at its peak, it needs:

1. **Context** — what the agent **knows**
2. **Environment** — what the agent **can do**

These are different layers, and they're often confused.

**Without context**, the agent doesn't know what to do. You have to re-explain everything every session. The agent feels powerful in theory and useless in practice.

**Without environment**, the agent knows but can't act. It generates plans, suggestions, summaries — but you still have to copy-paste, run commands, file results manually. You become the agent's hands.

**With both**, you have an agent.

A useful analogy:

| | Brain | Body | Person |
|---|---|---|---|
| Provides | knowledge, memory, judgment | hands, tools, mobility | action in the world |
| Without the other | inert | random | nonexistent |

| | Context | Environment | Agent |
|---|---|---|---|
| Provides | facts, history, procedures, identity | filesystem, APIs, commands, web | useful work |
| Without the other | pure information | pure capability | nothing |

---

## What most frameworks ship

Look at the popular agent frameworks: LangChain, CrewAI, AutoGen, LlamaIndex, Haystack, Microsoft Semantic Kernel. They differ in style but all converge on the same shape:

- They give you ways to wrap APIs as **tools**
- They give you ways to **orchestrate** model calls
- They give you ways to define **workflows** between tools
- They give you ways to run **multi-step plans**

This is **environment**. They make it easier for an agent to *act*.

What they don't give you is **context infrastructure**. They assume you'll build it yourself, via:

- Prompt engineering (re-explain every session)
- Vector databases (semantic search over docs)
- RAG pipelines (retrieve relevant chunks at runtime)
- System prompts (static identity, no growth)

These work, but they're brittle:

- **Prompt engineering** doesn't scale across months
- **Vector search** is fuzzy — it surfaces what's *similar*, not what's *true*
- **RAG** is a pipeline you have to maintain, not a system that grows
- **System prompts** are frozen identities, not living memory

The result: powerful agents that forget who they're talking to, what they decided last week, and where the project stands.

## What Claude Code already gives you

Anthropic's Claude Code already provides **excellent environment**:

- Filesystem read/write
- Bash / shell execution
- Web fetch / web search
- MCP integrations (Slack, Gmail, Linear, Drive, Canva, GitHub, dozens more)
- Subagents (specialists you can spawn)
- Hooks (automatic actions on session events)
- Slash commands (custom workflows)
- Built-in conversation memory

If you're using Claude Code, you don't need another environment layer. You need **context**.

## What SolverOS ships

SolverOS is the **context infrastructure** that makes Claude Code's environment shine:

- **Editorial filesystem** — every project carries its own `CLAUDE.md`, `historico.md`, `objetivos.md` that the agent reads and absorbs as context
- **Structured log** — every decision, bugfix, discovery is registered in SQLite with a type, date, and project, queryable forever
- **Procedural skills** — repeatable procedures with clear triggers, captured as code the agent runs (not docs the agent might read)
- **Auto-loaded session context** — a hook injects active objectives, recent activity, and open issues at session boot

Together, this means: when you open Claude Code, your agent already knows where you stopped, what's pending, what's decided, and what tools are available to act.

The combination:

```
SolverOS (context)  +  Claude Code (environment)  =  Useful agent
```

---

## Why filesystem?

The choice of *filesystem as substrate* is deliberate. Three reasons:

### 1. The filesystem is universal

Every operating system has one. Every dev tool reads it. Every LLM that runs locally can access it. No vendor lock-in. No cloud dependency. No subscription. No API rate limits.

Your agent's memory is yours, on your disk, in plain text and SQLite. You can read it with `cat`, query it with `sqlite3`, version it with `git`, sync it with Dropbox, audit it with `grep`.

### 2. The filesystem is observable

When the agent's memory is buried in a vector database, you can't read it. You can't `git diff` last month's decisions vs this month's. You can't grep for a project name and see every entry related to it.

When memory is files + SQLite, **everything is observable**. You can audit what the agent thinks. You can correct mistakes. You can rollback. You can trust because you can verify.

### 3. The filesystem is the OS

Your computer already runs on a filesystem. Your projects are folders. Your documents are files. Your tools are programs that read and write files.

SolverOS doesn't add a new abstraction layer. It uses the substrate that already exists. **Your computer becomes the agent's environment** — not a sandbox, not a container, not a virtual workspace.

This is the deepest design choice in SolverOS. **Most agent frameworks isolate the agent from your real system.** SolverOS inverts that — your real system *is* where the agent lives.

This scares people used to virtualenvs and Docker. It's also what unlocks the productivity. The agent works on real files, in real folders, with real consequences. No simulation, no replay buffer, no synthetic environment.

---

## Why SQLite?

For the structured log (`pmo.db`), we use SQLite. Three reasons:

1. **Zero infrastructure.** SQLite is one file. No server, no setup, no port. Just a file.
2. **Zero external dependency.** Works offline, on a plane, without internet, without an API key.
3. **Auditable.** Open it with any SQL tool. Browse it. Query it. Export it. Backup it with `cp`.

The trade-off: not multi-user. For teams, each person has their own workspace, sync via git. For individuals — which is who SolverOS is for — SQLite is perfect.

---

## Why skills as code, not docs?

Skills are procedural — they're code the agent runs, not documentation the agent reads.

The difference matters:

- **Documentation** describes *how*, but execution depends on the agent inferring intent every time
- **Skills as code** specify *exactly* what to do, with predictable inputs and outputs

When you have a procedure you do every week ("review my PDFs and find what I should read"), encoding it as a skill means:

- The agent runs it identically every time
- You can update the procedure once, and every future invocation benefits
- The skill is testable, version-able, shareable
- The output format is predictable

Docs are for humans. Skills are for agents. SolverOS has both — but the procedures live in skills, not docs.

---

## What this enables

When context lives in the filesystem and gets auto-loaded into Claude Code:

- **Your agent has continuity.** It picks up where you stopped, even after weeks
- **Your agent has identity.** It knows who you are, what you're working on, what matters
- **Your agent has accountability.** Every decision has a timestamp, a type, a project link
- **Your agent grows.** Every skill you add, every procedure you encode, every project you finish — all of it accumulates

You stop being the copy-paste between the chat and your filesystem. You become the strategist; the agent becomes the operator.

---

## What this is NOT

Some clarifications, because the framing invites misunderstanding:

### SolverOS is not AGI infrastructure

It's a productivity tool. A pragmatic one. It doesn't make Claude smarter. It just stops Claude from being amnesiac about your work.

### SolverOS is not a replacement for Claude memory

Claude Code has its own memory layer (in `~/.claude/`). That layer is about *you* — your preferences, your jeito, your style. SolverOS is about your *work* — projects, decisions, history. They complement each other.

### SolverOS is not for everyone

If you have one project and chat with Claude weekly, SolverOS is overkill. If you operate 5+ projects in parallel and lose context constantly, SolverOS is a multiplier. Self-select.

### SolverOS is not a framework

Frameworks have classes you inherit, runtimes you boot, lifecycles you respect. SolverOS has files you organize and SQL you query. The whole thing fits in your head in 30 minutes.

---

## Inspirations

The thinking behind SolverOS draws on:

- **[Building a Second Brain (Tiago Forte)](https://www.buildingasecondbrain.com/)** — for the editorial approach to personal knowledge
- **[Andy Matuschak's notes](https://notes.andymatuschak.org/)** — for atomic notes and tools-for-thought
- **[Plain text accounting (ledger, beancount)](https://plaintextaccounting.org/)** — for the *plain text + tools* aesthetic
- **[Unix philosophy](https://en.wikipedia.org/wiki/Unix_philosophy)** — small tools, composable, do one thing well
- **[Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)** — for *bounded contexts* mapping cleanly to *project folders*

If you're building agent infrastructure, study these too.

---

## Why are commands in Portuguese?

This is asked enough to deserve an answer in the philosophy doc.

SolverOS was built by a Brazilian operator (Fernando Solver) over 90+ days of running Claude Code on his own work. The commands and skills carry the names he naturally uses — `/comecar` instead of `/start`, `revisar-semana` instead of `weekly-review`.

Three reasons we kept it that way:

1. **Authenticity.** This isn't a product designed for a market — it's a system that grew from real use. Renaming everything to English would be retrofitting a different identity over a working tool.

2. **Names are surface, not substance.** Slash commands and skills are just markdown files. Anyone can rename them in 30 seconds without touching the engine. The value isn't in the words; it's in the system.

3. **Better to commit honestly than to compromise weakly.** A half-translated product (some commands EN, some PT) would be worse than either pure option. So we picked one — and made the other trivially achievable for anyone who wants it.

That said: **multi-language support is planned for v0.7** — first-class English, Spanish, and other locale stacks where every command, skill, and message is available natively in your language. Until then, the names are Portuguese, and you have a translation table in the README.

If you can read this paragraph, you can use SolverOS. The Portuguese is decoration.

---

## Where this goes next

SolverOS Core is the foundation. The future is **stacks** — domain-specific extensions that build on top:

- **Stack Empresa** — generic enterprise PMO
- **Stack Ecommerce** — for Brazilian e-commerce operators
- **Stack Consultor** — for knowledge sellers (mentors, coaches, educators)
- **Stack Indústria** — for small manufacturing
- **Stack Serviços** — for agencies, clinics, professional services

Each stack adds vocabulary, commands, skills, and templates appropriate to its domain. The Core stays generic. The whole thing stays composable.

---

## A final note

This document defends a thesis. The thesis might be wrong in 18 months — the field moves fast, and what looks like the right substrate today might be obsolete tomorrow.

But the right way to test it is to **use it**. Build with it. Push it. Find where it breaks.

If you find SolverOS useful, share it. If you find it broken, file an issue. If you build something on top of it, ship a stack. That's how a thesis becomes a tool.

> *Crie um agente. Em uma pasta. Em menos de 1 minuto.*
> *Build an agent. In a folder. In under a minute.*

—

*Written in continuous collaboration between Fernando Solver and Claude (Anthropic).*
