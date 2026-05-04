"""
pmo_tokens - Agregador de consumo de tokens do Claude Code.

Varre ~/.claude/projects/<workspace>/*.jsonl (transcripts do Claude Code)
e soma tokens por workspace. Workspace aqui = raiz onde o usuario abriu o
Claude Code (cwd no momento da sessao).

Uso:
    from pmo_tokens import tokens_by_workspace, tokens_totals
    ws = tokens_by_workspace()             # todos os periodos
    ws = tokens_by_workspace(days=30)      # ultimos 30 dias
    totals = tokens_totals(ws)             # agregado geral
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta


def _claude_projects_dir() -> Path:
    """Diretorio padrao onde Claude Code grava transcripts."""
    home = Path(os.environ.get('CLAUDE_HOME') or str(Path.home()))
    return home / '.claude' / 'projects'


def _short_name(folder_name: str) -> str:
    """
    Nome amigavel do workspace. Remove prefixo de drive e trunca se muito
    longo (mostra inicio e fim com reticencias).
    """
    for prefix in ('C--', 'D--', 'E--', 'F--'):
        if folder_name.startswith(prefix):
            folder_name = folder_name[len(prefix):]
            break
    if len(folder_name) > 46:
        return folder_name[:22] + '…' + folder_name[-20:]
    return folder_name


def _decode_path_hint(folder_name: str) -> str:
    """
    Tentativa aproximada de recuperar o path original.
    Nao e perfeita (o encoding do Claude Code perde distincao entre '-' e '/'),
    mas serve como hint no tooltip.
    """
    for letter in ('C', 'D', 'E', 'F'):
        pref = letter + '--'
        if folder_name.startswith(pref):
            return letter + ':/' + folder_name[len(pref):].replace('-', '/')
    return folder_name


def tokens_by_workspace(days: int = None, claude_projects_dir: str = None) -> list:
    """
    Agrega tokens por workspace a partir dos transcripts do Claude Code.

    Args:
        days: se informado, considera somente mensagens com timestamp
              >= (hoje - days). Default: todo o historico.
        claude_projects_dir: override do diretorio. Default:
              ~/.claude/projects/

    Returns:
        Lista ordenada por total desc, cada item:
          {
            'workspace': str,       # nome do folder encoded
            'path_hint': str,       # path decodificado (aproximacao)
            'short': str,           # nome curto para exibicao
            'input': int,
            'output': int,
            'cache_read': int,
            'cache_creation': int,
            'total': int,
            'sessions': int,        # numero de arquivos .jsonl com usage
            'messages': int,        # numero de mensagens assistant com usage
            'first_activity': str,  # ISO timestamp
            'last_activity': str,   # ISO timestamp
          }
        Lista vazia se o diretorio nao existir.
    """
    root = Path(claude_projects_dir) if claude_projects_dir else _claude_projects_dir()
    if not root.exists() or not root.is_dir():
        return []

    cutoff = None
    if days is not None:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    result = []
    for wks_dir in root.iterdir():
        if not wks_dir.is_dir():
            continue
        agg = dict(
            input=0, output=0, cache_read=0, cache_creation=0,
            sessions=0, messages=0,
            first_activity=None, last_activity=None,
        )
        for jsonl in wks_dir.glob('*.jsonl'):
            had_usage = False
            try:
                with open(jsonl, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        if '"usage"' not in line:
                            continue
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        ts = obj.get('timestamp')
                        if cutoff and ts and ts < cutoff:
                            continue
                        msg = obj.get('message', {}) or {}
                        usage = msg.get('usage', {}) or {}
                        if not usage:
                            continue
                        agg['input'] += usage.get('input_tokens') or 0
                        agg['output'] += usage.get('output_tokens') or 0
                        agg['cache_read'] += usage.get('cache_read_input_tokens') or 0
                        agg['cache_creation'] += usage.get('cache_creation_input_tokens') or 0
                        agg['messages'] += 1
                        had_usage = True
                        if ts:
                            if not agg['first_activity'] or ts < agg['first_activity']:
                                agg['first_activity'] = ts
                            if not agg['last_activity'] or ts > agg['last_activity']:
                                agg['last_activity'] = ts
                if had_usage:
                    agg['sessions'] += 1
            except Exception:
                continue

        total = agg['input'] + agg['output'] + agg['cache_read'] + agg['cache_creation']
        if total == 0:
            continue
        agg['workspace'] = wks_dir.name
        agg['path_hint'] = _decode_path_hint(wks_dir.name)
        agg['short'] = _short_name(wks_dir.name)
        agg['total'] = total
        result.append(agg)

    result.sort(key=lambda x: x['total'], reverse=True)
    return result


def tokens_totals(workspaces: list) -> dict:
    """Soma tokens de uma lista de workspaces (resultado de tokens_by_workspace)."""
    keys = ('input', 'output', 'cache_read', 'cache_creation', 'messages', 'sessions')
    agg = {k: 0 for k in keys}
    for w in workspaces:
        for k in keys:
            agg[k] += w.get(k, 0) or 0
    agg['total'] = agg['input'] + agg['output'] + agg['cache_read'] + agg['cache_creation']
    agg['workspaces'] = len(workspaces)
    # Taxa de cache hit = cache_read / (cache_read + input + cache_creation)
    paid_input = agg['input'] + agg['cache_creation']
    denom = paid_input + agg['cache_read']
    agg['cache_hit_rate'] = (agg['cache_read'] / denom) if denom > 0 else 0.0
    return agg


if __name__ == '__main__':
    ws = tokens_by_workspace(days=30)
    t = tokens_totals(ws)
    print(f"[INFO] {len(ws)} workspaces com tokens nos ultimos 30 dias")
    print(f"[INFO] Total: {t['total']:,} tokens (in={t['input']:,} out={t['output']:,} "
          f"cache_r={t['cache_read']:,} cache_w={t['cache_creation']:,})")
    print(f"[INFO] Cache hit rate: {t['cache_hit_rate']*100:.1f}%")
    print()
    print(f"{'#':>3}  {'WORKSPACE':<48} {'TOTAL':>14} {'SESSIONS':>9} {'MSGS':>6}")
    for i, w in enumerate(ws[:15], 1):
        print(f"{i:>3}  {w['short']:<48} {w['total']:>14,} {w['sessions']:>9} {w['messages']:>6}")
