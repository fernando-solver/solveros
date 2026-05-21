# Security Policy

## Supported versions

We support security fixes for the **latest minor version** only.

| Version | Supported |
|---------|-----------|
| 0.6.x   | ✅ |
| < 0.6   | ❌ |

## Reporting a vulnerability

If you find a security vulnerability in SolverOS, **please do not open a public issue.**

Instead, email: **fernando@icarus.com.br**

Include:
- Description of the vulnerability
- Steps to reproduce
- Affected version(s)
- Potential impact
- Suggested fix (if you have one)

## Response timeline

- **Initial response:** within 7 days
- **Confirmed assessment:** within 14 days
- **Fix released (if confirmed):** within 30 days for critical, 60 days for moderate

## What counts as a security vulnerability

- Code execution from untrusted input (skill files, manifest.yaml, etc)
- Credential leakage in `pmo_share.py` scrub
- Path traversal in `pmo_setup.py` or `pmo_stacks.py`
- SQLite injection in `pmo_db.py`
- Hook execution that could be abused (`pmo_hooks/`)

## What does NOT count

- Bugs that don't affect security (those go in regular issues)
- Issues with Claude Code itself (report those to Anthropic)
- Issues with your local Python or OS configuration

## Acknowledgments

Reporters of confirmed vulnerabilities will be credited in [AUTHORS.md](AUTHORS.md) and the relevant `CHANGELOG.md` entry, unless they prefer to remain anonymous.

Thanks for keeping SolverOS users safe.
