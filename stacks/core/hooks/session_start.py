"""SessionStart hook do Solverkitty.

Roda automaticamente quando Claude Code abre sessao no workspace. Imprime
contexto da marca ativa pra stdout (Claude Code agrega ao contexto).

Falha gracioso: try/except global. Hook NUNCA trava boot do Claude Code.
"""

import os
import sys
import traceback
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(ROOT)


def _print(*args):
    """Print pra stdout flushando — Claude Code captura."""
    print(*args, flush=True)


def _read_active_brand():
    """Le slug da marca ativa do lockfile, ou None."""
    lockfile = os.path.join(WORKSPACE, ".solver-active-brand")
    if not os.path.isfile(lockfile):
        return None
    try:
        with open(lockfile, encoding="utf-8") as f:
            slug = f.read().strip()
        return slug or None
    except OSError:
        return None


def _safe_session_start():
    """Cria sessao no pmo.db. Retorna session_id ou None."""
    try:
        sys.path.insert(0, WORKSPACE)
        from pmo_db import session_start
        return session_start("auto via SessionStart hook")
    except Exception as e:
        _print(f"[Solverkitty hook] session_start falhou: {e}", file=sys.stderr)
        return None


def _load_brand_context(slug):
    """Imprime resumo do estado da marca ativa."""
    try:
        sys.path.insert(0, WORKSPACE)
        from pmo_db import (
            cliente_get, objetivo_progress, objetivos_em_risco,
            metricas_periodo,
        )
        from datetime import date, timedelta

        cliente = cliente_get(slug)
        if not cliente:
            _print(f"[Solverkitty] Marca ativa '{slug}' nao encontrada no pmo.db.")
            return

        cid = cliente["id"]
        nome = cliente.get("nome") or slug
        segmento = cliente.get("segmento") or "—"

        _print(f"## Marca ativa: {nome}")
        _print(f"- slug: {slug} | segmento: {segmento}")
        _print(f"- pasta: clientes/{slug}/")

        # Objetivos
        objs = objetivo_progress(cid)
        em_risco = [o for o in objs if o.get("pct") is not None and o["pct"] < 0.7]
        if em_risco:
            _print(f"- objetivos em risco ({len(em_risco)}/{len(objs)}):")
            for o in em_risco[:3]:
                pct = o.get("pct") or 0
                _print(f"    * {o.get('tipo')}: {pct*100:.0f}% do alvo | {o.get('descricao') or ''}")
        elif objs:
            _print(f"- {len(objs)} objetivo(s) ativo(s), sem riscos")

        # Metricas dos ultimos 30d
        di = (date.today() - timedelta(days=30)).isoformat()
        df = date.today().isoformat()
        m = metricas_periodo(cid, di, df)
        if m.get("investimento"):
            inv = m.get("investimento") or 0
            rec = m.get("receita") or 0
            roas = m.get("roas")
            _print(f"- ultimos 30d: invest R$ {inv:,.0f} | receita R$ {rec:,.0f}"
                   + (f" | ROAS {roas:.2f}x" if roas else ""))
    except Exception as e:
        _print(f"[Solverkitty hook] _load_brand_context falhou: {e}", file=sys.stderr)


def _load_recent_activity():
    """Imprime ultimas 3 atividades do workspace."""
    try:
        sys.path.insert(0, WORKSPACE)
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
        slug = _read_active_brand()

        _print(f"# Solverkitty | sessao {sid or '?'} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        if slug:
            _load_brand_context(slug)
        else:
            _print("\nNenhuma empresa ativa. Use /setup-empresa pra cadastrar.")

        _load_recent_activity()

    except Exception:
        # Falha silenciosa — hook nunca trava o boot.
        _print("[Solverkitty hook] erro nao tratado:", file=sys.stderr)
        _print(traceback.format_exc(), file=sys.stderr)


if __name__ == "__main__":
    main()
