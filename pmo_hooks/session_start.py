"""SessionStart hook do Solverkitty.

Roda automaticamente quando Claude Code abre sessao no workspace.
Imprime contexto do trabalho em curso pra stdout (Claude Code agrega
ao contexto da sessao).

Falha gracioso: try/except global. Hook NUNCA trava boot do Claude Code.
"""

import os
import sys
import traceback
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(ROOT)


def _print(*args, **kwargs):
    """Print pra stdout flushando — Claude Code captura."""
    print(*args, flush=True, **kwargs)


def _safe_session_start():
    """Cria sessao no pmo.db. Retorna session_id ou None."""
    try:
        sys.path.insert(0, WORKSPACE)
        from pmo_db import session_start
        return session_start("auto via SessionStart hook")
    except Exception as e:
        _print(f"[Solverkitty hook] session_start falhou: {e}", file=sys.stderr)
        return None


def _load_objective():
    """Imprime objetivo principal e progresso, se houver."""
    try:
        sys.path.insert(0, WORKSPACE)
        from pmo_db import objetivo_list

        objetivos = objetivo_list()
        principal = next(
            (o for o in objetivos if o.get('tipo') == 'meta_30_dias'),
            None
        )

        if principal:
            desc = principal.get('descricao') or '(sem descricao)'
            prazo = principal.get('prazo') or 'sem prazo'
            _print(f"\n## Objetivo principal")
            _print(f"- {desc}")
            _print(f"- prazo: {prazo}")
        elif objetivos:
            _print(f"\n## Objetivos ativos: {len(objetivos)}")
            _print("(nenhum marcado como principal — defina um com `meta_30_dias`)")
    except Exception as e:
        _print(f"[Solverkitty hook] _load_objective falhou: {e}", file=sys.stderr)


def _load_recent_activity():
    """Imprime ultimas 3 atividades do workspace."""
    try:
        import sqlite3
        db = os.path.join(WORKSPACE, "pmo.db")
        if not os.path.isfile(db):
            return
        con = sqlite3.connect(db)
        rows = con.execute(
            "SELECT date, project, type, summary FROM activities "
            "ORDER BY id DESC LIMIT 3"
        ).fetchall()
        con.close()
        if rows:
            _print("\n## Ultimas atividades")
            for date_, proj, type_, summary in rows:
                _print(f"- {date_} [{type_}] {proj}: {summary[:80]}")
    except Exception as e:
        _print(f"[Solverkitty hook] _load_recent_activity falhou: {e}", file=sys.stderr)


def main():
    try:
        sid = _safe_session_start()

        _print(
            f"# Solverkitty | sessao {sid or '?'} | "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        _load_objective()
        _load_recent_activity()

        # Se workspace esta vazio (sem objetivos nem atividades), sugere setup
        try:
            sys.path.insert(0, WORKSPACE)
            from pmo_db import objetivo_list
            if not objetivo_list():
                _print(
                    "\nWorkspace ainda nao configurado. "
                    "Rode `/comecar` pra setup inicial em ~5 minutos."
                )
        except Exception:
            pass

    except Exception:
        # Falha silenciosa — hook nunca trava o boot.
        _print("[Solverkitty hook] erro nao tratado:", file=sys.stderr)
        _print(traceback.format_exc(), file=sys.stderr)


if __name__ == "__main__":
    main()
