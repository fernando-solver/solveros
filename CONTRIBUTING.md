# Contributing to Solverkitty

Thanks for considering contributing! Solverkitty grows when people use it for real work and share what they learned.

## TL;DR

The most valuable contributions, in order:

1. **Use Solverkitty for real work, file the rough edges as issues.**
2. **Add your use case to [SHOWCASE.md](SHOWCASE.md)** — it helps others see fit.
3. **Submit a skill** for something you automated.
4. **Submit a stack** for your domain (consulting, research, sales, etc).
5. **Improve docs** — clearer wording, missing examples, broken links.
6. **Submit code fixes** for bugs you encountered.

## Types of contributions

### 🐛 Bug reports

Use the [bug report issue template](.github/ISSUE_TEMPLATE/bug_report.md). Include:
- Your OS + Python version + Claude Code version
- Exact steps to reproduce
- What you expected vs what happened
- Logs from `pmo_hooks/session_start.py` if relevant

### 💡 Feature requests

Use the [feature request issue template](.github/ISSUE_TEMPLATE/feature_request.md). Before submitting:
- Search existing issues — someone may have already proposed it
- Explain the *why* before the *what*
- Mention your real use case — generic requests get deprioritized

### 🎨 New skills

Skills are the easiest way to extend Solverkitty. To submit one:

1. Read existing skills in `skills/` for the pattern
2. Use the frontmatter format:
   ```yaml
   ---
   name: skill_name_in_snake_case
   description: One-line summary
   trigger: When this skill should run (free text)
   version: 1
   last_updated: YYYY-MM-DD
   uses_count: 0
   ---
   ```
3. Include `## When to use` and `## When NOT to use` sections
4. Provide a concrete `## Procedure` with copy-paste-ready code
5. Submit a PR with the skill in `skills/` AND in the appropriate `stacks/<stack>/skills/`

### 🏗️ New stacks

Stacks add domain-specific capabilities (commands, skills, agents, templates).

To create a stack:

1. Create `stacks/<your-stack-name>/`
2. Add `manifest.yaml` (see `stacks/core/manifest.yaml` for the format)
3. Add the structure expected:
   ```
   stacks/<your-stack>/
   ├── manifest.yaml
   ├── _template/        # what gets copied to a new project
   ├── commands/          # slash commands
   ├── skills/            # procedural skills
   ├── agents/            # subagents (optional)
   └── hooks/             # custom hooks (optional)
   ```
4. Document the stack in a `README.md` inside the stack folder
5. Submit a PR

A stack is **accepted** when:
- It serves a clear vertical (research, e-commerce, consulting, etc)
- It has at least 3 skills + 1 command + 1 template
- It doesn't conflict with Core conventions
- The author has used it for real work for at least 30 days

### 📝 Documentation

Docs improvements are always welcome. Particularly valuable:
- Adding examples to existing skills
- Translating documentation to other languages
- Fixing broken links
- Clarifying confusing sections

### 🔧 Code contributions

Before opening a PR with code changes:

1. **Open an issue first** for non-trivial changes
2. Check that `python -m py_compile` passes for any Python file you change
3. Match existing code style (PEP 8 with Brazilian flexibility — comments in pt-BR or EN both fine)
4. Update `CHANGELOG.md` with your change
5. Add tests if you're adding logic (we accept simple `assert` based tests)

## Pull request process

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature` or `fix/your-fix`
3. Make your changes
4. Run smoke tests:
   ```bash
   for f in pmo_*.py pmo_hooks/*.py; do python -m py_compile "$f"; done
   ```
5. Commit with a descriptive message
6. Open the PR using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
7. Wait for review — first response usually within 7 days

### Commit message format

We use a loose convention inspired by [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

<optional longer description>

<optional Co-Authored-By>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`

Example:
```
feat(skills): add skill_pessoal_06_planejar-semana

Generates a structured weekly plan based on the user's main objective
and the previous week's review output.
```

## Code style

- **Python:** PEP 8, but no enforcement of line length (readable beats short)
- **Markdown:** GitHub-flavored, headers in sentence case
- **Console output:** ASCII only (no emojis or unicode in `print()` — Windows cp1252 breaks)
- **File output:** UTF-8 with BOM for CSVs (`utf-8-sig`), regular UTF-8 for everything else
- **Names:** snake_case for files, files start with `pmo_` or `skill_pessoal_`

## What we DON'T accept

- Features that require external services beyond Claude Code + Python stdlib + SQLite
- Skills that depend on paid APIs (we want zero-cost barrier to entry)
- Code that mixes business logic between Core and Stacks (Core stays generic)
- Refactors with no functional improvement
- Changes that break backward compatibility without strong justification

## Questions?

Open a [Discussion](https://github.com/fernando-solver/solverkitty/discussions) or DM [@fernandosolver](https://instagram.com/fernandosolver) on Instagram.

## Recognition

All contributors get listed in [AUTHORS.md](AUTHORS.md). Significant contributions are mentioned in `CHANGELOG.md` with proper attribution.

---

By contributing, you agree your contributions will be licensed under the MIT License.
