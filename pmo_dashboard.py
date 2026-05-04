"""
PMO Dashboard - Gera dashboard HTML estatico a partir do pmo.db.

Uso pelo Claude Code:
    python -c "from pmo_dashboard import generate_dashboard; print(generate_dashboard())"

Por padrao gera um HTML auto-contido em `dashboard.html` na raiz do workspace
(sobrescreve a cada rodada — mantem o atalho sempre no mesmo lugar).

Design: editorial tecnico. Paleta creme/tinta com acento terracota unico,
tipografia Fraunces (display serif) + JetBrains Mono (tabular). Sem
gradientes AI-genericos, sem cards com sombra, rules finos estilo jornal.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from pmo_tokens import tokens_by_workspace, tokens_totals
from pmo_db import (
    db_stats,
    project_stats,
    heatmap_data,
    hours_per_day,
    activities_by_month,
    sessions_start_hour_distribution,
    sessions_per_week,
    projects_touched_per_week,
    themes_top,
    shares_log,
    list_objectives,
    objective_dashboard,
    query_activities,
    list_pending,
    session_last,
)

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
CHART_LOCAL = BASE_DIR / 'assets' / 'chart.min.js'
CHART_CDN = 'https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js'


def has_chart_local() -> bool:
    return CHART_LOCAL.is_file()


def _gather_data():
    stats = db_stats()
    projs = project_stats()
    top_projects = sorted(projs, key=lambda p: p['total_activities'], reverse=True)[:10]
    month_acts = query_activities("date >= date('now', 'start of month')", (), 1000)
    type_dist = {}
    for a in query_activities("1=1", (), 10000):
        type_dist[a['type']] = type_dist.get(a['type'], 0) + 1
    heatmap = heatmap_data(days=90)
    hours = hours_per_day(days=60)
    by_month = activities_by_month(months=5)
    hour_dist = sessions_start_hour_distribution(days=90)
    sess_per_week = sessions_per_week(weeks=12)
    projs_per_week = projects_touched_per_week(weeks=12)
    themes = themes_top(n=25, since_days=90)
    obj_dashboard = objective_dashboard()
    shares = shares_log(limit=20)
    pendings = list_pending()
    last_sess = session_last()

    # Tokens: periodo longo (90 dias) + top workspaces por consumo
    try:
        tokens_ws = tokens_by_workspace(days=90)
        tokens_total_30 = tokens_totals(tokens_by_workspace(days=30))
        tokens_total_90 = tokens_totals(tokens_ws)
    except Exception:
        tokens_ws = []
        tokens_total_30 = {}
        tokens_total_90 = {}

    now = datetime.now()
    return {
        'generated_at': now.strftime('%Y-%m-%d %H:%M'),
        'generated_at_iso': now.isoformat(),
        'generated_edition': now.strftime('%d.%m.%Y').upper(),
        'stats': stats,
        'top_projects': top_projects,
        'month_activities_count': len(month_acts),
        'type_dist': type_dist,
        'heatmap': heatmap,
        'hours_per_day': hours,
        'activities_by_month': by_month,
        'hour_dist': hour_dist,
        'sess_per_week': sess_per_week,
        'projs_per_week': projs_per_week,
        'themes': themes,
        'objectives': obj_dashboard,
        'shares': shares,
        'pendings_count': len(pendings),
        'last_session': last_sess,
        'tokens_ws': tokens_ws,
        'tokens_total_30': tokens_total_30,
        'tokens_total_90': tokens_total_90,
    }


def _render_html(data: dict) -> str:
    if has_chart_local():
        try:
            chart_js_code = CHART_LOCAL.read_text(encoding='utf-8')
            chart_script = f"<script>{chart_js_code}</script>"
        except Exception:
            chart_script = f'<script src="{CHART_CDN}"></script>'
    else:
        chart_script = f'<script src="{CHART_CDN}"></script>'

    data_json = json.dumps(data, ensure_ascii=False, default=str)
    data_json = data_json.replace('</script>', '<\\/script>')

    return HTML_TEMPLATE.format(
        chart_script=chart_script,
        data_json=data_json,
        generated_at=data['generated_at'],
        generated_edition=data['generated_edition'],
    )


def generate_dashboard(output_path: str = None, open_browser: bool = False) -> str:
    """
    Gera dashboard HTML estatico.

    Args:
        output_path: caminho de saida. Default: `dashboard.html` na raiz do workspace
                     (sobrescreve a cada rodada, serve como atalho fixo).
        open_browser: se True, abre no browser padrao apos gerar

    Returns:
        Path (absoluto, posix-like) do HTML gerado.
    """
    data = _gather_data()
    html = _render_html(data)

    if output_path is None:
        output_path = BASE_DIR / 'dashboard.html'
    else:
        output_path = Path(output_path).resolve()

    output_path.write_text(html, encoding='utf-8')
    abs_path = str(output_path).replace('\\', '/')

    if open_browser:
        import webbrowser
        webbrowser.open(f'file:///{abs_path}')

    return abs_path


# ============================================================
# TEMPLATE HTML — estetica editorial tecnica
# ============================================================

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PMO / Solver Filesystem — Edicao de {generated_edition}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,700;0,9..144,900;1,9..144,400;1,9..144,500&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
__CHART_SCRIPT_PLACEHOLDER__
<style>
  :root {{
    --paper: #f5f2ea;
    --paper-deep: #ece6d4;
    --ink: #1a1510;
    --ink-soft: #6b5d4f;
    --ink-faint: #a89a85;
    --rule: #d4c9b8;
    --accent: #c45a2f;
    --accent-deep: #8a3c1c;
    --accent-soft: rgba(196, 90, 47, 0.12);
    --pos: #3d6b3a;
    --neg: #a8322a;
    --display: 'Fraunces', 'Iowan Old Style', 'Georgia', serif;
    --mono: 'JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', monospace;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html, body {{
    background: var(--paper);
    color: var(--ink);
    font-family: var(--mono);
    font-size: 13px;
    line-height: 1.55;
    font-feature-settings: "tnum" 1, "ss01" 1;
  }}

  body {{
    background:
      radial-gradient(ellipse at 18% 8%, rgba(196,90,47,0.04) 0%, transparent 55%),
      radial-gradient(ellipse at 85% 90%, rgba(26,21,16,0.035) 0%, transparent 60%),
      var(--paper);
    min-height: 100vh;
    background-attachment: fixed;
  }}

  /* Textura de grao sutil sobre fundo */
  body::before {{
    content: '';
    position: fixed; inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: 0.35;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.10 0 0 0 0 0.08 0 0 0 0 0.06 0 0 0 0.06 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
  }}

  .wrap {{
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: min(1560px, 96vw);
    margin: 0 auto;
    padding: 72px 64px 96px;
  }}

  /* ---------- HEADER MASTHEAD ---------- */
  .masthead {{
    border-top: 3px double var(--ink);
    border-bottom: 1px solid var(--ink);
    padding: 22px 0 20px;
    margin-bottom: 44px;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: baseline;
    gap: 32px;
  }}

  .brand {{
    font-family: var(--display);
    font-weight: 900;
    font-size: 46px;
    line-height: 1;
    letter-spacing: -0.02em;
    font-variation-settings: 'opsz' 144, 'SOFT' 30;
  }}
  .brand em {{
    font-style: italic;
    font-weight: 500;
    color: var(--accent);
  }}

  .masthead-middle {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-soft);
    text-align: center;
    line-height: 1.6;
  }}
  .masthead-middle span {{
    display: block;
  }}
  .masthead-middle .sep {{
    color: var(--ink-faint);
    margin: 4px 0;
  }}

  .masthead-right {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-soft);
    text-align: right;
    line-height: 1.6;
  }}
  .masthead-right strong {{
    color: var(--ink);
    font-weight: 600;
    font-size: 11px;
  }}

  /* ---------- FRESHNESS TICKER ---------- */
  .ticker {{
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 10px 0;
    border-bottom: 1px solid var(--rule);
    margin-bottom: 56px;
    display: flex;
    gap: 28px;
    align-items: center;
    color: var(--ink-soft);
  }}
  .ticker .dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--pos);
    animation: pulse 2.4s infinite;
  }}
  .ticker.warn .dot {{ background: #c2821f; }}
  .ticker.stale .dot {{ background: var(--neg); animation: none; }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.5; transform: scale(1.3); }}
  }}
  .ticker code {{
    background: var(--accent-soft);
    color: var(--accent-deep);
    padding: 2px 8px;
    border-radius: 2px;
    font-size: 10px;
    text-transform: none;
    letter-spacing: 0;
  }}
  .ticker .stretch {{ flex: 1; }}

  /* ---------- SECTION HEADER ---------- */
  .section-head {{
    display: grid;
    grid-template-columns: 80px 1fr auto;
    align-items: baseline;
    gap: 24px;
    padding-bottom: 12px;
    margin-bottom: 28px;
    border-bottom: 1px solid var(--ink);
  }}
  .section-num {{
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 0.2em;
    color: var(--accent);
    font-weight: 600;
  }}
  .section-title {{
    font-family: var(--display);
    font-weight: 500;
    font-size: 30px;
    font-style: italic;
    letter-spacing: -0.01em;
    line-height: 1;
    font-variation-settings: 'opsz' 144;
  }}
  .section-meta {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--ink-faint);
  }}
  section {{
    margin-bottom: 72px;
  }}

  /* ---------- KPI ROW ---------- */
  .kpi-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    margin-bottom: 48px;
    border-top: 1px solid var(--ink);
    border-bottom: 1px solid var(--ink);
  }}
  .kpi {{
    padding: 24px 28px 22px;
    border-right: 1px solid var(--rule);
    position: relative;
  }}
  .kpi:last-child {{ border-right: none; }}
  .kpi-num {{
    font-family: var(--display);
    font-weight: 400;
    font-size: 58px;
    line-height: 1;
    letter-spacing: -0.02em;
    font-variation-settings: 'opsz' 144;
    margin-bottom: 6px;
  }}
  .kpi-num.accent {{ color: var(--accent); font-style: italic; }}
  .kpi-label {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--ink-soft);
  }}

  /* ---------- CALENDAR layout §01 — grid 2x2 editorial ---------- */
  .cal-layout {{
    display: grid;
    grid-template-columns: 1fr 1px 1fr;
    grid-template-rows: auto 1px auto;
    /* sem gap — padding nas cells controla o ar */
  }}
  .cell-tl {{
    grid-column: 1; grid-row: 1;
    padding: 0 56px 40px 0;
  }}
  .cell-tr {{
    grid-column: 3; grid-row: 1;
    padding: 0 0 40px 56px;
  }}
  .cell-bl {{
    grid-column: 1; grid-row: 3;
    padding: 40px 56px 0 0;
  }}
  .cell-br {{
    grid-column: 3; grid-row: 3;
    padding: 40px 0 0 56px;
  }}
  .cell-divider-v {{
    grid-column: 2; grid-row: 1 / span 3;
    background: var(--rule);
    align-self: stretch;
  }}
  .cell-divider-h {{
    grid-column: 1 / -1; grid-row: 2;
    background: var(--rule);
    height: 1px;
  }}
  .cell-kicker {{
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 18px;
  }}

  /* ---------- CALENDAR (layout v2 — legado, nao usado atualmente) ---------- */
  /*
     Grid 2x3: [heatmap] [divider] [chart-lateral]
               [------] [-------] [------------]
               [chart-abaixo-esq]            [chart-abaixo-dir]
  */
  .cal-layout-v2 {{
    display: grid;
    grid-template-columns: auto 1px 1fr;
    grid-template-rows: auto auto auto;
    gap: 32px 36px;
    align-items: stretch;
    margin-bottom: 40px;
  }}
  .cal-layout-v2 > .cal-panel {{ grid-column: 1; grid-row: 1; }}
  .cal-layout-v2 > .cal-v-divider {{
    grid-column: 2; grid-row: 1;
    background: var(--rule);
    width: 1px; align-self: stretch;
  }}
  .cal-layout-v2 > #chart-hours-wrap {{ grid-column: 3; grid-row: 1; }}
  .cal-layout-v2 > .cal-h-divider {{
    grid-column: 1 / 4; grid-row: 2;
    height: 1px; background: var(--rule);
    align-self: stretch;
  }}
  .cal-layout-v2 > .cal-h-divider.right-side {{ display: none; }}
  .cal-layout-v2 > .mini-chart:not(#chart-hours-wrap) {{ grid-row: 3; }}

  .cal-panel {{ min-width: 0; align-self: start; }}

  /* Mini chart cards — mesma estetica editorial, sem background */
  .mini-chart {{
    display: flex;
    flex-direction: column;
    min-width: 0;
  }}
  .mini-chart-label {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--ink-soft);
    border-bottom: 1px solid var(--rule);
    padding-bottom: 8px;
    margin-bottom: 14px;
  }}
  .mini-chart-canvas {{
    position: relative;
    height: 160px;
    flex: 1;
  }}
  .mini-chart-canvas.tall {{ height: 180px; }}
  .mini-chart-hint {{
    font-family: var(--mono);
    font-size: 10px;
    color: var(--ink-faint);
    margin-top: 10px;
    letter-spacing: 0.04em;
  }}
  .mini-chart-hint strong {{
    color: var(--ink);
    font-weight: 500;
  }}
  .mini-chart-hint em {{
    color: var(--accent);
    font-style: normal;
    font-weight: 500;
  }}

  /* Seção §02 — Ritmo operacional (3 mini-graficos) */
  .ritmo-grid {{
    display: grid;
    grid-template-columns: 1fr 1px 1fr 1px 1fr;
    gap: 32px;
    align-items: stretch;
  }}
  .ritmo-divider {{
    background: var(--rule);
    align-self: stretch;
    width: 1px;
  }}

  /* Linha horizontal de mini-stats abaixo da secao 01 (legado — nao usada atualmente) */
  .sk-row {{
    display: grid;
    grid-template-columns: 1fr 1.4fr 1fr;
    gap: 0;
    border-top: 1px solid var(--ink);
    border-bottom: 1px solid var(--ink);
    padding: 0;
  }}
  .sk-row .sk {{
    padding: 24px 28px;
    border-right: 1px solid var(--rule);
  }}
  .sk-row .sk:last-child {{ border-right: none; }}
  .sk-row .sk-label {{
    border-bottom: none;
    padding-bottom: 0;
    margin-bottom: 10px;
    font-size: 10px;
    letter-spacing: 0.2em;
  }}

  .cal-wrap {{
    display: grid;
    grid-template-columns: 30px auto;
    gap: 8px;
    width: fit-content;
    --cell: 22px;
    --gap: 4px;
  }}
  .cal-days {{
    display: grid;
    grid-template-rows: repeat(7, var(--cell));
    gap: var(--gap);
    padding-top: 22px;
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-faint);
    align-items: center;
  }}
  .cal-grid-wrap {{ display: flex; flex-direction: column; }}
  .cal-months {{
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--ink-soft);
    height: 18px;
    position: relative;
  }}
  .cal-month {{ position: absolute; white-space: nowrap; }}
  .cal-grid {{
    display: grid;
    grid-template-rows: repeat(7, var(--cell));
    grid-auto-flow: column;
    grid-auto-columns: var(--cell);
    gap: var(--gap);
  }}
  .cal-cell {{
    width: var(--cell);
    height: var(--cell);
    background: var(--paper-deep);
    transition: transform 0.12s ease;
    opacity: 0;
    animation: cellIn 0.5s cubic-bezier(.2,.7,.3,1) forwards;
  }}
  .cal-cell.empty {{ visibility: hidden; }}
  .cal-cell.l1 {{ background: rgba(196, 90, 47, 0.22); }}
  .cal-cell.l2 {{ background: rgba(196, 90, 47, 0.42); }}
  .cal-cell.l3 {{ background: rgba(196, 90, 47, 0.62); }}
  .cal-cell.l4 {{ background: rgba(196, 90, 47, 0.82); }}
  .cal-cell.l5 {{ background: var(--accent-deep); }}
  .cal-cell:hover {{ transform: scale(1.6); z-index: 2; outline: 1px solid var(--ink); }}
  @keyframes cellIn {{
    from {{ opacity: 0; transform: scale(0.7); }}
    to {{ opacity: 1; transform: scale(1); }}
  }}

  .cal-legend {{
    margin-top: 16px;
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ink-faint);
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .cal-legend .swatches {{ display: flex; gap: 3px; }}
  .cal-legend .swatches span {{
    display: inline-block; width: 12px; height: 12px;
  }}

  /* Top row do calendario: heatmap + crescimento mensal ao lado */
  .cal-top-row {{
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 80px;
    align-items: start;
  }}
  .cal-heatmap-block {{ min-width: 0; }}
  .cal-growth-block {{
    min-width: 0;
    padding-top: 14px; /* alinha topo com cal-months do heatmap */
  }}
  .cal-growth-label {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--ink-soft);
    border-bottom: 1px solid var(--rule);
    padding-bottom: 8px;
    margin-bottom: 14px;
  }}
  .growth-bars {{
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}
  .growth-row {{
    display: grid;
    grid-template-columns: 40px 1fr auto;
    gap: 16px;
    align-items: center;
  }}
  .growth-label {{
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--ink-soft);
    text-align: right;
  }}
  .growth-bar-wrap {{
    height: 18px;
    background: transparent;
    position: relative;
  }}
  .growth-bar {{
    height: 100%;
    background: var(--ink);
    opacity: 0.85;
    transform-origin: left;
    animation: growBar 0.9s cubic-bezier(.2,.7,.3,1) forwards;
  }}
  .growth-bar.peak {{ background: var(--accent); opacity: 1; }}
  .growth-value {{
    font-family: var(--display);
    font-size: 18px;
    font-weight: 500;
    color: var(--ink);
    letter-spacing: -0.01em;
    min-width: 52px;
    text-align: right;
    font-variation-settings: 'opsz' 144;
  }}
  .growth-row.peak-row .growth-value {{ color: var(--accent); font-style: italic; }}
  .growth-row.peak-row .growth-label {{ color: var(--accent); font-weight: 600; }}
  .cal-growth-hint {{
    font-family: var(--display);
    font-style: italic;
    font-size: 13px;
    color: var(--ink-faint);
    margin-top: 16px;
    line-height: 1.5;
  }}
  .cal-growth-hint strong {{
    font-style: normal;
    color: var(--accent);
    font-weight: 500;
  }}
  @keyframes growBar {{
    from {{ transform: scaleX(0); }}
    to {{ transform: scaleX(1); }}
  }}

  /* Lead editorial narrativo + cards tipograficos (embaixo do heatmap) */
  .cal-lead {{
    font-family: var(--display);
    font-style: italic;
    font-size: 18px;
    line-height: 1.55;
    color: var(--ink-soft);
    margin-bottom: 28px;
    max-width: 560px;
    letter-spacing: -0.005em;
  }}
  .cal-lead strong {{
    font-style: normal;
    font-weight: 500;
    color: var(--accent);
    letter-spacing: -0.01em;
  }}
  .cal-lead em {{
    font-style: italic;
    color: var(--ink);
    font-weight: 500;
  }}

  .cal-cards {{
    display: grid;
    grid-template-columns: 1fr 1px 1fr 1px 1fr;
    gap: 0;
    padding-top: 22px;
    border-top: 1px solid var(--rule);
  }}
  .cal-card {{
    padding: 0 18px 0 0;
  }}
  .cal-card:not(:first-child) {{ padding-left: 24px; }}
  .cal-card:last-child {{ padding-right: 0; }}
  .cal-card-value {{
    font-family: var(--display);
    font-size: 38px;
    font-weight: 400;
    line-height: 1;
    letter-spacing: -0.02em;
    font-variation-settings: 'opsz' 144;
    margin-bottom: 10px;
    color: var(--ink);
  }}
  .cal-card-value em {{
    font-family: var(--display);
    font-style: italic;
    font-size: 17px;
    color: var(--ink-faint);
    font-weight: 400;
    margin-left: 4px;
    letter-spacing: 0;
  }}
  .cal-card-value strong {{
    font-family: var(--display);
    font-style: italic;
    font-weight: 500;
    color: var(--accent);
  }}
  .cal-card-label {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-soft);
    line-height: 1.4;
  }}
  .cal-card-divider {{
    background: var(--rule);
    width: 1px;
  }}

  /* Sidekpi — legado vertical (nao usado) */
  .cal-side {{
    display: flex;
    flex-direction: column;
    gap: 32px;
  }}
  /* Sidekpi horizontal (BR do grid 2x2) */
  .cal-side-horiz {{
    display: grid;
    grid-template-columns: 1fr 1px 1.2fr 1px 1fr;
    gap: 0;
    align-items: start;
  }}
  .cal-side-horiz > .sk {{
    padding: 0 20px;
  }}
  .cal-side-horiz > .sk:first-child {{ padding-left: 0; }}
  .cal-side-horiz > .sk:last-child {{ padding-right: 0; }}
  .sk-divider {{
    background: var(--rule);
    width: 1px;
    align-self: stretch;
  }}
  .cal-side-horiz .sk-value {{ font-size: 38px; }}
  .cal-side-horiz .dow-bars {{ height: 32px; }}
  .sk {{ }}
  .sk-label {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--ink-soft);
    border-bottom: 1px solid var(--rule);
    padding-bottom: 6px;
    margin-bottom: 14px;
  }}
  .sk-value {{
    font-family: var(--display);
    font-weight: 400;
    font-size: 44px;
    line-height: 1;
    letter-spacing: -0.02em;
    font-variation-settings: 'opsz' 144;
  }}
  .sk-value em {{ font-style: italic; color: var(--accent); font-weight: 500; }}
  .sk-hint {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.06em;
    color: var(--ink-faint);
    margin-top: 8px;
  }}

  .dow-bars {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-top: 12px;
    align-items: end;
    height: 40px;
  }}
  .dow-bar {{
    background: var(--ink-soft);
    min-height: 2px;
  }}
  .dow-bar.peak {{ background: var(--accent); }}
  .dow-labels {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-faint);
    margin-top: 6px;
    text-align: center;
  }}

  .trend-big {{
    font-family: var(--display);
    font-size: 38px;
    font-weight: 500;
    letter-spacing: -0.02em;
    line-height: 1;
  }}
  .trend-big.up {{ color: var(--pos); }}
  .trend-big.down {{ color: var(--neg); }}
  .trend-big.flat {{ color: var(--ink-soft); }}
  .trend-arrow {{
    font-family: var(--mono);
    font-weight: 600;
    font-size: 22px;
    margin-right: 8px;
  }}

  /* ---------- HOURS CHART ---------- */
  .chart-box {{
    position: relative;
    height: 220px;
    padding: 0 0 12px;
  }}
  .hours-summary {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    margin-top: 28px;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
  }}
  .hsum {{
    padding: 18px 20px;
    border-right: 1px solid var(--rule);
  }}
  .hsum:last-child {{ border-right: none; }}
  .hsum-label {{
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-soft);
    margin-bottom: 6px;
  }}
  .hsum-value {{
    font-family: var(--display);
    font-size: 26px;
    font-weight: 500;
    line-height: 1;
    letter-spacing: -0.01em;
  }}
  .hsum-hint {{
    font-family: var(--mono);
    font-size: 10px;
    color: var(--ink-faint);
    margin-top: 4px;
  }}

  /* ---------- TWO COLUMN GRID ---------- */
  .two-col {{
    display: grid;
    grid-template-columns: 1.4fr 1px 1fr;
    gap: 48px;
    align-items: start;
  }}
  .two-col .col-divider {{ background: var(--rule); align-self: stretch; min-height: 100%; }}

  /* Top projects: lista editorial */
  .proj-list {{ list-style: none; counter-reset: proj; }}
  .proj-item {{
    display: grid;
    grid-template-columns: 28px 1fr auto;
    gap: 16px;
    align-items: baseline;
    padding: 14px 0;
    border-bottom: 1px solid var(--rule);
  }}
  .proj-item:last-child {{ border-bottom: none; }}
  .proj-rank {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--ink-faint);
    letter-spacing: 0.1em;
  }}
  .proj-name {{
    font-family: var(--display);
    font-size: 16px;
    font-weight: 500;
    line-height: 1.3;
    color: var(--ink);
  }}
  .proj-count {{
    font-family: var(--mono);
    font-size: 13px;
    color: var(--ink);
    font-weight: 500;
  }}
  .proj-count em {{
    font-family: var(--mono);
    font-style: normal;
    color: var(--ink-faint);
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-left: 4px;
  }}

  /* Donut tipos */
  .donut-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }}
  .donut-canvas-wrap {{
    position: relative;
    width: 220px;
    height: 220px;
  }}
  .donut-legend {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px 18px;
    font-family: var(--mono);
    font-size: 11px;
    width: 100%;
  }}
  .donut-legend div {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .donut-legend .sw {{
    width: 10px; height: 10px;
    flex-shrink: 0;
  }}
  .donut-legend .name {{
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 10px;
    color: var(--ink-soft);
    flex: 1;
  }}
  .donut-legend .val {{
    font-weight: 500;
    color: var(--ink);
  }}

  /* Objetivos */
  .obj-list {{ display: flex; flex-direction: column; gap: 28px; }}
  .obj-card {{
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 8px 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--rule);
  }}
  .obj-card:last-child {{ border-bottom: none; }}
  .obj-title {{
    font-family: var(--display);
    font-weight: 500;
    font-size: 20px;
    line-height: 1.25;
    grid-column: 1 / -1;
  }}
  .obj-meta {{
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--ink-soft);
  }}
  .obj-meta .accent {{ color: var(--accent); }}
  .obj-progress-wrap {{
    grid-column: 1 / -1;
    margin-top: 6px;
  }}
  .obj-progress {{
    height: 2px;
    background: var(--rule);
    overflow: hidden;
    position: relative;
  }}
  .obj-progress-fill {{
    height: 100%;
    background: var(--accent);
    transform-origin: left;
  }}

  /* Temas cloud */
  .themes {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px 20px;
    align-items: baseline;
    line-height: 1.8;
  }}
  .theme {{
    font-family: var(--display);
    color: var(--ink);
    cursor: default;
    transition: color 0.15s;
  }}
  .theme:hover {{ color: var(--accent); font-style: italic; }}

  /* Shares table */
  table {{
    width: 100%;
    border-collapse: collapse;
    font-family: var(--mono);
    font-size: 12px;
  }}
  thead th {{
    text-align: left;
    padding: 10px 14px;
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-soft);
    border-bottom: 1px solid var(--ink);
    font-weight: 500;
  }}
  tbody td {{
    padding: 12px 14px;
    border-bottom: 1px solid var(--rule);
    color: var(--ink);
  }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover td {{ background: var(--accent-soft); }}

  .muted {{
    font-family: var(--display);
    font-style: italic;
    font-size: 15px;
    color: var(--ink-faint);
    padding: 24px 0;
  }}

  /* ---------- TOKENS §07 ---------- */
  .tk-wrap {{ display: flex; flex-direction: column; gap: 32px; }}
  .tk-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border-top: 1px solid var(--ink);
    border-bottom: 1px solid var(--ink);
  }}
  .tk-cell {{
    padding: 22px 24px;
    border-right: 1px solid var(--rule);
  }}
  .tk-cell:last-child {{ border-right: none; }}
  .tk-label {{
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--ink-soft);
    margin-bottom: 8px;
  }}
  .tk-value {{
    font-family: var(--display);
    font-size: 34px;
    font-weight: 400;
    line-height: 1;
    letter-spacing: -0.02em;
    font-variation-settings: 'opsz' 144;
  }}
  .tk-value.accent {{ color: var(--accent); font-style: italic; font-weight: 500; }}
  .tk-unit {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--ink-faint);
    font-weight: 400;
    letter-spacing: 0.08em;
    margin-left: 4px;
  }}
  .tk-hint {{
    font-family: var(--mono);
    font-size: 10px;
    color: var(--ink-faint);
    margin-top: 6px;
    letter-spacing: 0.04em;
  }}
  .tk-hint strong {{ color: var(--ink); font-weight: 500; }}

  /* Top workspaces list */
  .tk-list {{ list-style: none; }}
  .tk-item {{
    display: grid;
    grid-template-columns: 28px minmax(0, 1fr) 260px 110px 76px;
    gap: 24px;
    align-items: center;
    padding: 18px 0;
    border-bottom: 1px solid var(--rule);
  }}
  .tk-item:last-child {{ border-bottom: none; }}
  .tk-rank {{
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 0.1em;
    color: var(--ink-faint);
  }}
  .tk-name {{
    font-family: var(--display);
    font-size: 16px;
    font-weight: 500;
    line-height: 1.3;
    color: var(--ink);
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .tk-name em {{
    font-family: var(--mono);
    font-style: normal;
    font-size: 10px;
    letter-spacing: 0.1em;
    color: var(--ink-faint);
    display: block;
    font-weight: 400;
    margin-top: 2px;
    text-transform: none;
  }}
  .tk-total {{
    font-family: var(--display);
    font-size: 22px;
    font-weight: 500;
    line-height: 1;
    color: var(--ink);
    letter-spacing: -0.01em;
    text-align: right;
    min-width: 110px;
  }}
  .tk-total em {{
    font-family: var(--mono);
    font-style: normal;
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ink-faint);
    font-weight: 400;
    margin-left: 4px;
  }}
  /* Barra stacked por tipo de token */
  .tk-stack {{
    position: relative;
    height: 18px;
    background: var(--paper-deep);
    display: flex;
  }}
  .tk-stack > div {{
    height: 100%;
    transition: opacity 0.15s;
  }}
  .tk-stack:hover > div {{ opacity: 0.6; }}
  .tk-stack > div:hover {{ opacity: 1; }}
  .tk-stack .seg-cache_read {{ background: rgba(196, 90, 47, 0.25); }}
  .tk-stack .seg-cache_creation {{ background: rgba(196, 90, 47, 0.55); }}
  .tk-stack .seg-input {{ background: var(--accent-deep); }}
  .tk-stack .seg-output {{ background: var(--ink); }}
  .tk-msgs {{
    font-family: var(--mono);
    font-size: 10px;
    color: var(--ink-soft);
    letter-spacing: 0.06em;
    text-align: right;
    min-width: 76px;
  }}
  .tk-msgs strong {{ color: var(--ink); font-weight: 500; }}

  .tk-legend {{
    display: flex;
    gap: 24px;
    margin-top: 16px;
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ink-soft);
  }}
  .tk-legend .chip {{
    display: inline-block;
    width: 10px; height: 10px;
    margin-right: 6px;
    vertical-align: middle;
  }}

  /* Footer colophon */
  footer {{
    margin-top: 88px;
    padding-top: 24px;
    border-top: 3px double var(--ink);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 32px;
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--ink-soft);
    line-height: 1.8;
  }}
  footer code {{
    text-transform: none;
    letter-spacing: 0;
    background: var(--paper-deep);
    padding: 2px 6px;
    color: var(--ink);
  }}
  footer .right {{ text-align: right; color: var(--ink-faint); }}

  /* Staggered load */
  .reveal {{ opacity: 0; transform: translateY(8px); animation: rev 0.6s ease forwards; }}
  @keyframes rev {{ to {{ opacity: 1; transform: none; }} }}

  /* Responsivo basico */
  @media (max-width: 1100px) {{
    .cal-layout {{
      grid-template-columns: 1fr;
      grid-template-rows: auto auto auto auto;
    }}
    .cell-tl {{ grid-column: 1; grid-row: 1; padding: 0 0 32px 0; border-bottom: 1px solid var(--rule); }}
    .cell-tr {{ grid-column: 1; grid-row: 2; padding: 32px 0; border-bottom: 1px solid var(--rule); }}
    .cell-bl {{ grid-column: 1; grid-row: 3; padding: 32px 0; border-bottom: 1px solid var(--rule); }}
    .cell-br {{ grid-column: 1; grid-row: 4; padding: 32px 0 0 0; }}
    .cell-divider-v, .cell-divider-h {{ display: none; }}
    .cal-side-horiz {{ grid-template-columns: 1fr; }}
    .cal-side-horiz > .sk {{ padding: 16px 0; }}
    .cal-side-horiz .sk-divider {{ display: none; }}
    .ritmo-grid {{ grid-template-columns: 1fr; gap: 40px; }}
    .ritmo-divider {{ display: none; }}
    .two-col {{ grid-template-columns: 1fr; }}
    .two-col .col-divider {{ display: none; }}
    .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
    .kpi:nth-child(2) {{ border-right: none; }}
    .kpi:nth-child(-n+2) {{ border-bottom: 1px solid var(--rule); }}
    .hours-summary {{ grid-template-columns: repeat(2, 1fr); }}
    .hsum:nth-child(2) {{ border-right: none; }}
    .hsum:nth-child(-n+2) {{ border-bottom: 1px solid var(--rule); }}
    .sk-row {{ grid-template-columns: 1fr; }}
    .sk-row .sk {{ border-right: none; border-bottom: 1px solid var(--rule); }}
    .sk-row .sk:last-child {{ border-bottom: none; }}
  }}
  @media (max-width: 640px) {{
    .wrap {{ padding: 48px 24px 64px; }}
    .masthead {{ grid-template-columns: 1fr; gap: 12px; }}
    .brand {{ font-size: 34px; }}
    .kpi-row {{ grid-template-columns: 1fr; }}
    .kpi {{ border-right: none; border-bottom: 1px solid var(--rule); }}
  }}
</style>
</head>
<body>
<div class="wrap">

  <!-- MASTHEAD -->
  <header class="masthead">
    <div class="brand">pmo<em>/</em><br>solver</div>
    <div class="masthead-middle">
      <span>Retrato operacional do filesystem</span>
      <span class="sep">— § —</span>
      <span>Gerado a partir de pmo.db</span>
    </div>
    <div class="masthead-right">
      <strong>Edicao de {generated_edition}</strong><br>
      Revisao continua
    </div>
  </header>

  <!-- TICKER / FRESHNESS -->
  <div id="ticker" class="ticker">
    <span class="dot"></span>
    <span id="ticker-text">Carregando</span>
    <span class="stretch"></span>
    <span>Regerar: <code>python -c "from pmo_dashboard import generate_dashboard; generate_dashboard()"</code></span>
  </div>

  <!-- KPIs -->
  <div class="kpi-row reveal">
    <div class="kpi"><div class="kpi-num" id="kpi-projects">0</div><div class="kpi-label">Projetos registrados</div></div>
    <div class="kpi"><div class="kpi-num" id="kpi-sessions">0</div><div class="kpi-label">Sessoes totais</div></div>
    <div class="kpi"><div class="kpi-num accent" id="kpi-month-acts">0</div><div class="kpi-label">Atividades do mes</div></div>
    <div class="kpi"><div class="kpi-num" id="kpi-pendings">0</div><div class="kpi-label">Pendencias abertas</div></div>
  </div>

  <!-- CALENDARIO -->
  <section>
    <div class="section-head">
      <div class="section-num">§ 01</div>
      <div class="section-title">Calendario de atividade</div>
      <div class="section-meta">Ultimos 90 dias</div>
    </div>

    <div class="cal-layout">
      <!-- TL — DIARIO (heatmap) -->
      <div class="cell-tl">
        <div class="cell-kicker">Diario · 90 celulas</div>
        <div class="cal-wrap">
          <div class="cal-days">
            <div>Seg</div><div></div><div>Qua</div><div></div><div>Sex</div><div></div><div>Dom</div>
          </div>
          <div class="cal-grid-wrap">
            <div id="cal-months" class="cal-months"></div>
            <div id="cal-grid" class="cal-grid"></div>
          </div>
        </div>
        <div class="cal-legend">
          <span>Menos</span>
          <div class="swatches">
            <span style="background:var(--paper-deep)"></span>
            <span style="background:rgba(196,90,47,0.22)"></span>
            <span style="background:rgba(196,90,47,0.42)"></span>
            <span style="background:rgba(196,90,47,0.62)"></span>
            <span style="background:rgba(196,90,47,0.82)"></span>
            <span style="background:var(--accent-deep)"></span>
          </div>
          <span>Mais</span>
        </div>
      </div>

      <!-- divisor vertical (linha 1+2) -->
      <div class="cell-divider-v"></div>

      <!-- TR — MENSAL (crescimento) -->
      <div class="cell-tr">
        <div class="cell-kicker">Mensal · 6 meses</div>
        <div class="cal-growth-label">Crescimento mensal</div>
        <div id="cal-growth-bars" class="growth-bars"></div>
        <div class="cal-growth-hint" id="cal-growth-hint">&nbsp;</div>
      </div>

      <!-- divisor horizontal -->
      <div class="cell-divider-h"></div>

      <!-- BL — SINTESE (lead + cards) -->
      <div class="cell-bl">
        <div class="cell-kicker">Sintese do periodo</div>
        <p class="cal-lead" id="cal-lead">&nbsp;</p>
        <div class="cal-cards">
          <div class="cal-card">
            <div class="cal-card-value" id="cal-card-active">—</div>
            <div class="cal-card-label">Dias ativos</div>
          </div>
          <div class="cal-card-divider"></div>
          <div class="cal-card">
            <div class="cal-card-value" id="cal-card-peak">—</div>
            <div class="cal-card-label" id="cal-card-peak-label">Pico do periodo</div>
          </div>
          <div class="cal-card-divider"></div>
          <div class="cal-card">
            <div class="cal-card-value" id="cal-card-longest">—</div>
            <div class="cal-card-label">Streak maximo</div>
          </div>
        </div>
      </div>

      <!-- BR — PRESENTE (3 mini-stats horizontais) -->
      <div class="cell-br">
        <div class="cell-kicker">Presente</div>
        <div class="cal-side-horiz">
          <div class="sk">
            <div class="sk-label">Streak atual</div>
            <div class="sk-value" id="stat-streak">—</div>
            <div class="sk-hint" id="stat-streak-hint">dias consecutivos</div>
          </div>
          <div class="sk-divider"></div>
          <div class="sk">
            <div class="sk-label">Dia da semana</div>
            <div class="sk-value" id="stat-dow">—</div>
            <div class="dow-bars" id="stat-dow-bars"></div>
            <div class="dow-labels">
              <div>S</div><div>T</div><div>Q</div><div>Q</div><div>S</div><div>S</div><div>D</div>
            </div>
          </div>
          <div class="sk-divider"></div>
          <div class="sk">
            <div class="sk-label">Tendencia · 4 sem</div>
            <div id="stat-trend" class="trend-big flat">—</div>
            <div class="sk-hint" id="stat-trend-hint">vs. 4 sem anteriores</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- RITMO OPERACIONAL (novos 3 graficos) -->
  <section>
    <div class="section-head">
      <div class="section-num">§ 02</div>
      <div class="section-title">Ritmo operacional</div>
      <div class="section-meta">Quando · quanto · com que variedade</div>
    </div>
    <div class="ritmo-grid">
      <div class="mini-chart">
        <div class="mini-chart-label">Hora de inicio · 90 dias</div>
        <div class="mini-chart-canvas tall"><canvas id="chart-hour-dist"></canvas></div>
        <div class="mini-chart-hint" id="chart-hour-hint">—</div>
      </div>
      <div class="ritmo-divider"></div>
      <div class="mini-chart">
        <div class="mini-chart-label">Sessoes por semana · 12 sem</div>
        <div class="mini-chart-canvas tall"><canvas id="chart-sess-week"></canvas></div>
        <div class="mini-chart-hint" id="chart-sess-hint">—</div>
      </div>
      <div class="ritmo-divider"></div>
      <div class="mini-chart">
        <div class="mini-chart-label">Projetos tocados por semana · 12 sem</div>
        <div class="mini-chart-canvas tall"><canvas id="chart-projs-week"></canvas></div>
        <div class="mini-chart-hint" id="chart-projs-hint">—</div>
      </div>
    </div>
  </section>

  <!-- HORAS POR DIA -->
  <section>
    <div class="section-head">
      <div class="section-num">§ 03</div>
      <div class="section-title">Horas trabalhadas por dia</div>
      <div class="section-meta">60 dias · cap 16h/sessao · 18h/dia</div>
    </div>
    <div class="chart-box">
      <canvas id="hours-bar"></canvas>
    </div>
    <div class="hours-summary" id="hours-summary"></div>
  </section>

  <!-- TOP PROJETOS + TIPOS -->
  <section>
    <div class="section-head">
      <div class="section-num">§ 04</div>
      <div class="section-title">Onde a atencao foi parar</div>
      <div class="section-meta">Agregados do log</div>
    </div>
    <div class="two-col">
      <div>
        <h3 style="font-family: var(--mono); font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--ink-soft); margin-bottom: 18px;">Top projetos por volume</h3>
        <ol id="top-projects" class="proj-list"></ol>
      </div>
      <div class="col-divider"></div>
      <div>
        <h3 style="font-family: var(--mono); font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--ink-soft); margin-bottom: 18px;">Distribuicao por tipo</h3>
        <div class="donut-wrap">
          <div class="donut-canvas-wrap"><canvas id="type-donut"></canvas></div>
          <div id="donut-legend" class="donut-legend"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- OBJETIVOS -->
  <section>
    <div class="section-head">
      <div class="section-num">§ 05</div>
      <div class="section-title">Objetivos estrategicos</div>
      <div class="section-meta">Progresso declarado</div>
    </div>
    <div id="objectives" class="obj-list"></div>
  </section>

  <!-- TEMAS -->
  <section>
    <div class="section-head">
      <div class="section-num">§ 06</div>
      <div class="section-title">Temas recorrentes</div>
      <div class="section-meta">Extraidos das descricoes · 90 dias</div>
    </div>
    <div id="themes" class="themes"></div>
  </section>

  <!-- SHARES -->
  <section>
    <div class="section-head">
      <div class="section-num">§ 07</div>
      <div class="section-title">Compartilhamentos recentes</div>
      <div class="section-meta">Exports curados / handoffs</div>
    </div>
    <div id="shares-table"></div>
  </section>

  <!-- TOKENS -->
  <section>
    <div class="section-head">
      <div class="section-num">§ 08</div>
      <div class="section-title">Consumo de tokens</div>
      <div class="section-meta">Transcripts do Claude Code · ultimos 30/90 dias</div>
    </div>
    <div id="tokens-block"></div>
  </section>

  <footer>
    <div>
      Dashboard gerado por <code>pmo_dashboard.py</code> · fonte <code>pmo.db</code><br>
      Solver Filesystem · log e autoridade
    </div>
    <div class="right">
      Fraunces · JetBrains Mono<br>
      Paleta creme/tinta · acento terracota
    </div>
  </footer>

</div>

<script>
const DATA = {data_json};

// ---------- TICKER ----------
(function() {{
  const el = document.getElementById('ticker');
  const txt = document.getElementById('ticker-text');
  const gen = new Date(DATA.generated_at_iso);
  const now = new Date();
  const minutes = Math.floor((now - gen) / 60000);
  let ago, cls;
  if (minutes < 60) {{
    ago = minutes <= 1 ? 'agora mesmo' : `ha ${{minutes}} minutos`;
    cls = '';
  }} else if (minutes < 60 * 24) {{
    ago = `ha ${{Math.floor(minutes/60)}}h`;
    cls = '';
  }} else if (minutes < 60 * 24 * 3) {{
    ago = `ha ${{Math.floor(minutes/60/24)}} dia(s)`;
    cls = 'warn';
  }} else {{
    ago = `ha ${{Math.floor(minutes/60/24)}} dias`;
    cls = 'stale';
  }}
  el.className = 'ticker ' + cls;
  txt.innerHTML = `Atualizado <strong style="color:var(--ink)">${{ago}}</strong> · ${{DATA.generated_at}}`;
}})();

// ---------- KPIs ----------
document.getElementById('kpi-projects').textContent = (DATA.stats.projects || 0);
document.getElementById('kpi-sessions').textContent = (DATA.stats.sessions || 0);
document.getElementById('kpi-month-acts').textContent = (DATA.month_activities_count || 0);
document.getElementById('kpi-pendings').textContent = (DATA.pendings_count || 0);

// ---------- CALENDARIO ----------
(function() {{
  const grid = document.getElementById('cal-grid');
  const monthsEl = document.getElementById('cal-months');
  const raw = DATA.heatmap || {{}};
  const dates = Object.keys(raw).sort();
  if (dates.length === 0) return;

  const level = (n) => {{
    if (!n) return '';
    if (n === 1) return 'l1';
    if (n <= 3) return 'l2';
    if (n <= 6) return 'l3';
    if (n <= 10) return 'l4';
    return 'l5';
  }};

  const items = dates.map(d => {{
    const dt = new Date(d + 'T00:00:00');
    let dow = dt.getDay() - 1;
    if (dow < 0) dow = 6;
    return {{ date: d, dt: dt, count: raw[d], dow: dow }};
  }});

  const firstDow = items[0].dow;
  for (let i = 0; i < firstDow; i++) {{
    const c = document.createElement('div');
    c.className = 'cal-cell empty';
    grid.appendChild(c);
  }}

  const MESES = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
  const monthMarks = {{}};
  let lastColIdx = 0;
  items.forEach((it, i) => {{
    const colIdx = Math.floor((firstDow + i) / 7);
    lastColIdx = colIdx;
    const cell = document.createElement('div');
    cell.className = 'cal-cell ' + level(it.count);
    cell.title = `${{it.date}} · ${{it.count}} atividade${{it.count === 1 ? '' : 's'}}`;
    cell.style.animationDelay = (i * 0.008) + 's';
    grid.appendChild(cell);
    const mesKey = it.dt.getFullYear() + '-' + it.dt.getMonth();
    if (!monthMarks[mesKey]) {{
      monthMarks[mesKey] = {{ col: colIdx, label: MESES[it.dt.getMonth()] }};
    }}
  }});

  // 22 cell + 4 gap = 26px/col
  const COL_PX = 26;
  Object.values(monthMarks).forEach(m => {{
    const span = document.createElement('div');
    span.className = 'cal-month';
    span.style.left = (m.col * COL_PX) + 'px';
    span.textContent = m.label;
    monthsEl.appendChild(span);
  }});

  // ---------- Lead editorial + cards tipograficos ----------
  const MESES_LONGOS = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
  const totalAct = Object.values(raw).reduce((s,v)=>s+(v||0), 0);
  const activeDays = Object.values(raw).filter(v => v > 0).length;
  const totalDays = Object.keys(raw).length;
  // Pico
  let peakDate = '', peakCount = 0;
  Object.entries(raw).forEach(([d, c]) => {{ if (c > peakCount) {{ peakCount = c; peakDate = d; }} }});
  // Streak maximo historico dentro do periodo
  let longestStreak = 0, runStreak = 0;
  dates.forEach(d => {{
    if (raw[d] > 0) {{ runStreak++; if (runStreak > longestStreak) longestStreak = runStreak; }}
    else runStreak = 0;
  }});

  const fmtShort = (iso) => {{
    if (!iso) return '—';
    const dt = new Date(iso + 'T00:00:00');
    return dt.getDate() + ' ' + MESES_LONGOS[dt.getMonth()];
  }};

  const leadEl = document.getElementById('cal-lead');
  if (leadEl) {{
    if (totalAct === 0) {{
      leadEl.textContent = 'Sem atividade registrada no periodo.';
    }} else {{
      leadEl.innerHTML = `
        Em <em>90 dias</em>, voce esteve ativo em <strong>${{activeDays}} dias</strong>.
        O pico foi em <strong>${{fmtShort(peakDate)}}</strong> — ${{peakCount}} atividade${{peakCount === 1 ? '' : 's'}} em um unico dia.
        O streak mais longo do periodo: <strong>${{longestStreak}} dia${{longestStreak === 1 ? '' : 's'}}</strong> consecutivos.
      `;
    }}
  }}

  // Cards
  const cardActive = document.getElementById('cal-card-active');
  if (cardActive) cardActive.innerHTML = `${{activeDays}}<em>/ ${{totalDays}}</em>`;
  const cardPeak = document.getElementById('cal-card-peak');
  const cardPeakLabel = document.getElementById('cal-card-peak-label');
  if (cardPeak) cardPeak.innerHTML = peakDate ? fmtShort(peakDate) : '—';
  if (cardPeakLabel) cardPeakLabel.textContent = peakCount
    ? `Dia mais intenso · ${{peakCount}} ativ.`
    : 'Dia mais intenso';
  const cardLongest = document.getElementById('cal-card-longest');
  if (cardLongest) cardLongest.innerHTML = longestStreak > 0
    ? `${{longestStreak}}<em> dia${{longestStreak === 1 ? '' : 's'}}</em>`
    : '—';
}})();

// ---------- CRESCIMENTO MENSAL (ao lado do heatmap) ----------
(function() {{
  const host = document.getElementById('cal-growth-bars');
  const hintEl = document.getElementById('cal-growth-hint');
  if (!host) return;
  const data = DATA.activities_by_month || [];
  if (data.length === 0) {{
    host.innerHTML = '<p class="muted" style="padding: 8px 0;">Sem dados mensais.</p>';
    return;
  }}
  const maxVal = Math.max(...data.map(m => m.count), 1);
  const peakIdx = data.reduce((bi, m, i) => m.count > data[bi].count ? i : bi, 0);

  data.forEach((m, i) => {{
    const row = document.createElement('div');
    row.className = 'growth-row' + (i === peakIdx && m.count > 0 ? ' peak-row' : '');
    const pct = (m.count / maxVal) * 100;
    const barCls = 'growth-bar' + (i === peakIdx && m.count > 0 ? ' peak' : '');
    row.innerHTML = `
      <div class="growth-label">${{m.label}}</div>
      <div class="growth-bar-wrap">
        <div class="${{barCls}}" style="width: ${{pct}}%; animation-delay: ${{i * 120}}ms;"></div>
      </div>
      <div class="growth-value">${{m.count.toLocaleString('pt-BR')}}</div>
    `;
    row.title = `${{m.ym}}: ${{m.count}} atividades`;
    host.appendChild(row);
  }});

  // Hint narrativo: compara primeiro mes nao-vazio com o pico
  const firstNonZero = data.find(m => m.count > 0);
  const peak = data[peakIdx];
  if (firstNonZero && peak && peak.count > 0 && firstNonZero !== peak) {{
    const growth = Math.round((peak.count / firstNonZero.count));
    hintEl.innerHTML = `De ${{firstNonZero.label}} a ${{peak.label}}: curva multiplicou <strong>${{growth}}×</strong>.`;
  }} else if (peak && peak.count > 0) {{
    hintEl.innerHTML = `Pico em <strong>${{peak.label}}</strong> · ${{peak.count}} atividades.`;
  }} else {{
    hintEl.textContent = '';
  }}
}})();

// ---------- MINI-STATS TEMPORAIS ----------
(function() {{
  const raw = DATA.heatmap || {{}};
  const dates = Object.keys(raw).sort();
  if (dates.length === 0) return;

  const DOW_NAMES = ['Segunda','Terca','Quarta','Quinta','Sexta','Sabado','Domingo'];

  // Streak
  let streak = 0;
  let streakBrokenAt = null;
  for (let i = dates.length - 1; i >= 0; i--) {{
    const d = dates[i];
    if (raw[d] > 0) streak++;
    else {{ streakBrokenAt = d; break; }}
  }}
  const streakEl = document.getElementById('stat-streak');
  streakEl.innerHTML = `<em>${{streak}}</em> <span style="font-size:22px;color:var(--ink-soft);font-style:italic;">${{streak === 1 ? 'dia' : 'dias'}}</span>`;
  const hintEl = document.getElementById('stat-streak-hint');
  if (streak === 0) hintEl.textContent = 'nenhum dia ativo recente';
  else if (streakBrokenAt) hintEl.textContent = 'desde ' + streakBrokenAt;
  else hintEl.textContent = 'ativo em todo o periodo';

  // Dia da semana
  const byDow = [0,0,0,0,0,0,0];
  dates.forEach(d => {{
    const dt = new Date(d + 'T00:00:00');
    let dow = dt.getDay() - 1;
    if (dow < 0) dow = 6;
    byDow[dow] += raw[d];
  }});
  const maxDow = Math.max(...byDow);
  const peakDow = byDow.indexOf(maxDow);
  document.getElementById('stat-dow').textContent = DOW_NAMES[peakDow];
  const barsEl = document.getElementById('stat-dow-bars');
  byDow.forEach((v, i) => {{
    const bar = document.createElement('div');
    bar.className = 'dow-bar' + (i === peakDow ? ' peak' : '');
    bar.style.height = maxDow > 0 ? ((v / maxDow) * 100) + '%' : '2px';
    bar.title = DOW_NAMES[i] + ' · ' + v + ' atividades';
    barsEl.appendChild(bar);
  }});

  // Tendencia
  const last4 = dates.slice(-28).reduce((s, d) => s + raw[d], 0);
  const prev4 = dates.slice(-56, -28).reduce((s, d) => s + raw[d], 0);
  const trendEl = document.getElementById('stat-trend');
  const trendHint = document.getElementById('stat-trend-hint');
  if (prev4 === 0 && last4 === 0) {{
    trendEl.textContent = '—';
    trendEl.className = 'trend-big flat';
    trendHint.textContent = 'sem dados suficientes';
  }} else if (prev4 === 0) {{
    trendEl.innerHTML = '<span class="trend-arrow">↗</span>novo';
    trendEl.className = 'trend-big up';
    trendHint.textContent = last4 + ' atividades em 4 semanas';
  }} else {{
    const pct = Math.round(((last4 - prev4) / prev4) * 100);
    let arrow, cls;
    if (pct > 5) {{ arrow = '↗'; cls = 'up'; }}
    else if (pct < -5) {{ arrow = '↘'; cls = 'down'; }}
    else {{ arrow = '→'; cls = 'flat'; }}
    trendEl.innerHTML = `<span class="trend-arrow">${{arrow}}</span>${{pct > 0 ? '+' : ''}}${{pct}}%`;
    trendEl.className = 'trend-big ' + cls;
    trendHint.textContent = last4 + ' vs ' + prev4 + ' atividades';
  }}
}})();

// ---------- HORA DE INICIO (distribuicao 24h) ----------
(function() {{
  const canvas = document.getElementById('chart-hour-dist');
  const hintEl = document.getElementById('chart-hour-hint');
  if (!canvas || typeof Chart === 'undefined') return;
  const dist = DATA.hour_dist || {{}};
  const hours = [];
  const values = [];
  for (let h = 0; h < 24; h++) {{
    hours.push(h);
    values.push(dist[h] || dist[String(h)] || 0);
  }}
  const total = values.reduce((a,b) => a+b, 0);
  if (total === 0) {{
    canvas.parentElement.innerHTML = '<p class="muted">Sem sessoes no periodo.</p>';
    hintEl.textContent = '';
    return;
  }}
  const max = Math.max(...values);
  const peakHour = values.indexOf(max);
  const colors = values.map((v, i) => i === peakHour ? '#c45a2f' : '#1a1510');

  // Buckets manha/tarde/noite para hint narrativo
  const morning = values.slice(5, 12).reduce((a,b)=>a+b,0);
  const afternoon = values.slice(12, 18).reduce((a,b)=>a+b,0);
  const evening = values.slice(18, 24).reduce((a,b)=>a+b,0);
  const night = values.slice(0, 5).reduce((a,b)=>a+b,0);
  const buckets = [
    {{name: 'manha', v: morning}}, {{name: 'tarde', v: afternoon}},
    {{name: 'noite', v: evening}}, {{name: 'madrugada', v: night}}
  ];
  buckets.sort((a,b) => b.v - a.v);

  new Chart(canvas, {{
    type: 'bar',
    data: {{
      labels: hours.map(h => String(h).padStart(2,'0') + 'h'),
      datasets: [{{
        data: values, backgroundColor: colors,
        borderRadius: 0, maxBarThickness: 8
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      animation: {{ duration: 700 }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: '#1a1510',
          titleFont: {{ family: 'JetBrains Mono', size: 10 }},
          bodyFont: {{ family: 'JetBrains Mono', size: 11 }},
          cornerRadius: 0, padding: 8,
          callbacks: {{
            title: (items) => String(items[0].parsed.x).padStart(2,'0') + ':00',
            label: (item) => item.parsed.y + ' sessao(oes)'
          }}
        }}
      }},
      scales: {{
        x: {{
          ticks: {{
            autoSkip: false,
            maxRotation: 0,
            callback: function(v) {{
              // Mostra so 0, 6, 12, 18
              const h = parseInt(this.getLabelForValue(v));
              return (h % 6 === 0) ? String(h).padStart(2,'0') + 'h' : '';
            }},
            font: {{ family: 'JetBrains Mono', size: 9 }},
            color: '#a89a85'
          }},
          grid: {{ display: false }}
        }},
        y: {{
          beginAtZero: true,
          ticks: {{
            precision: 0,
            font: {{ family: 'JetBrains Mono', size: 9 }},
            color: '#6b5d4f'
          }},
          grid: {{ color: '#d4c9b8', drawBorder: false }}
        }}
      }}
    }}
  }});

  hintEl.innerHTML = `Pico as <strong>${{String(peakHour).padStart(2,'0')}}h</strong> · maior concentracao de <em>${{buckets[0].name}}</em>`;
}})();

// ---------- SESSOES POR SEMANA ----------
(function() {{
  const canvas = document.getElementById('chart-sess-week');
  const hintEl = document.getElementById('chart-sess-hint');
  if (!canvas || typeof Chart === 'undefined') return;
  const weeks = DATA.sess_per_week || [];
  if (weeks.length === 0) {{
    canvas.parentElement.innerHTML = '<p class="muted">Sem dados.</p>'; return;
  }}
  const values = weeks.map(w => w.count);
  const labels = weeks.map(w => {{
    const d = new Date(w.week_start + 'T00:00:00');
    return String(d.getDate()).padStart(2,'0') + '/' + String(d.getMonth()+1).padStart(2,'0');
  }});
  const max = Math.max(...values);
  const colors = values.map(v => v === max && v > 0 ? '#c45a2f' : '#1a1510');

  new Chart(canvas, {{
    type: 'bar',
    data: {{ labels: labels, datasets: [{{
      data: values, backgroundColor: colors,
      borderRadius: 0, maxBarThickness: 18
    }}] }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      animation: {{ duration: 800 }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: '#1a1510',
          titleFont: {{ family: 'JetBrains Mono', size: 10 }},
          bodyFont: {{ family: 'JetBrains Mono', size: 11 }},
          cornerRadius: 0, padding: 8,
          callbacks: {{
            title: (items) => 'semana de ' + weeks[items[0].dataIndex].week_start,
            label: (item) => item.parsed.y + ' sessao(oes)'
          }}
        }}
      }},
      scales: {{
        x: {{
          ticks: {{
            maxRotation: 0,
            font: {{ family: 'JetBrains Mono', size: 9 }},
            color: '#a89a85'
          }},
          grid: {{ display: false }}
        }},
        y: {{
          beginAtZero: true,
          ticks: {{
            precision: 0,
            font: {{ family: 'JetBrains Mono', size: 9 }},
            color: '#6b5d4f'
          }},
          grid: {{ color: '#d4c9b8', drawBorder: false }}
        }}
      }}
    }}
  }});

  const total = values.reduce((a,b) => a+b, 0);
  const avg = (total / weeks.length).toFixed(1);
  const current = values[values.length - 1];
  const prev = values[values.length - 2] || 0;
  const delta = current - prev;
  const deltaTxt = delta > 0 ? `<em>+${{delta}}</em>` : delta < 0 ? `<em style="color:var(--neg)">${{delta}}</em>` : '<em style="color:var(--ink-faint)">=</em>';
  hintEl.innerHTML = `Media <strong>${{avg}}</strong>/sem · atual <strong>${{current}}</strong> ${{deltaTxt}} vs anterior`;
}})();

// ---------- PROJETOS TOCADOS POR SEMANA ----------
(function() {{
  const canvas = document.getElementById('chart-projs-week');
  const hintEl = document.getElementById('chart-projs-hint');
  if (!canvas || typeof Chart === 'undefined') return;
  const weeks = DATA.projs_per_week || [];
  if (weeks.length === 0) {{
    canvas.parentElement.innerHTML = '<p class="muted">Sem dados.</p>'; return;
  }}
  const values = weeks.map(w => w.count);
  const labels = weeks.map(w => {{
    const d = new Date(w.week_start + 'T00:00:00');
    return String(d.getDate()).padStart(2,'0') + '/' + String(d.getMonth()+1).padStart(2,'0');
  }});

  // Desenha como area/linha para diferenciar do bar ao lado
  new Chart(canvas, {{
    type: 'line',
    data: {{ labels: labels, datasets: [{{
      data: values,
      borderColor: '#c45a2f',
      backgroundColor: 'rgba(196, 90, 47, 0.12)',
      borderWidth: 2,
      pointRadius: 3,
      pointBackgroundColor: '#c45a2f',
      pointBorderColor: '#f5f2ea',
      pointBorderWidth: 1.5,
      tension: 0.32,
      fill: true
    }}] }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      animation: {{ duration: 900 }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: '#1a1510',
          titleFont: {{ family: 'JetBrains Mono', size: 10 }},
          bodyFont: {{ family: 'JetBrains Mono', size: 11 }},
          cornerRadius: 0, padding: 8,
          callbacks: {{
            title: (items) => 'semana de ' + weeks[items[0].dataIndex].week_start,
            label: (item) => item.parsed.y + ' projeto(s) tocado(s)'
          }}
        }}
      }},
      scales: {{
        x: {{
          ticks: {{
            maxRotation: 0,
            font: {{ family: 'JetBrains Mono', size: 9 }},
            color: '#a89a85'
          }},
          grid: {{ display: false }}
        }},
        y: {{
          beginAtZero: true,
          ticks: {{
            precision: 0,
            font: {{ family: 'JetBrains Mono', size: 9 }},
            color: '#6b5d4f'
          }},
          grid: {{ color: '#d4c9b8', drawBorder: false }}
        }}
      }}
    }}
  }});

  const avg = (values.reduce((a,b)=>a+b,0) / weeks.length).toFixed(1);
  const maxV = Math.max(...values);
  const current = values[values.length - 1];
  const label = current >= avg * 1.2 ? 'exploracao' : current <= avg * 0.8 ? 'foco' : 'equilibrio';
  hintEl.innerHTML = `Media <strong>${{avg}}</strong> proj./sem · pico <strong>${{maxV}}</strong> · atual <em>${{label}}</em>`;
}})();

// ---------- HORAS POR DIA ----------
(function() {{
  const canvas = document.getElementById('hours-bar');
  const summary = document.getElementById('hours-summary');
  const hpd = DATA.hours_per_day || {{}};
  const dates = Object.keys(hpd).sort();
  const values = dates.map(d => hpd[d]);

  if (typeof Chart === 'undefined') {{
    canvas.parentElement.innerHTML = '<p class="muted">Chart.js indisponivel.</p>';
    return;
  }}
  if (dates.length === 0 || values.every(v => v === 0)) {{
    canvas.parentElement.innerHTML = '<p class="muted">Nenhuma sessao encerrada com duracao mensuravel.</p>';
    return;
  }}

  let lastMonth = null;
  const MESES = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
  const labels = dates.map(d => {{
    const dt = new Date(d + 'T00:00:00');
    const m = dt.getMonth();
    const dd = String(dt.getDate()).padStart(2, '0');
    if (m !== lastMonth) {{
      lastMonth = m;
      return `${{dd}} ${{MESES[m]}}`;
    }}
    return dd;
  }});

  const INK = '#1a1510';
  const ACCENT = '#c45a2f';
  const RULE = '#d4c9b8';

  // Destaque da maior barra em accent
  const max = Math.max(...values);
  const barColors = values.map(v => v === max && v > 0 ? ACCENT : INK);

  new Chart(canvas, {{
    type: 'bar',
    data: {{
      labels: labels,
      datasets: [{{
        label: 'Horas',
        data: values,
        backgroundColor: barColors,
        borderRadius: 0,
        maxBarThickness: 12
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      animation: {{ duration: 800 }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: INK,
          titleFont: {{ family: 'JetBrains Mono', size: 11 }},
          bodyFont: {{ family: 'JetBrains Mono', size: 12 }},
          padding: 10,
          cornerRadius: 0,
          borderWidth: 0,
          callbacks: {{
            title: (items) => dates[items[0].dataIndex],
            label: (item) => item.parsed.y.toFixed(2) + ' h'
          }}
        }}
      }},
      scales: {{
        x: {{
          ticks: {{
            autoSkip: true, maxRotation: 0,
            font: {{ family: 'JetBrains Mono', size: 9 }},
            color: '#a89a85'
          }},
          grid: {{ display: false }}
        }},
        y: {{
          beginAtZero: true,
          ticks: {{
            callback: (v) => v + 'h',
            font: {{ family: 'JetBrains Mono', size: 10 }},
            color: '#6b5d4f'
          }},
          grid: {{ color: RULE, drawBorder: false }}
        }}
      }}
    }}
  }});

  const total = values.reduce((a,b) => a+b, 0);
  const active = values.filter(v => v > 0).length;
  const avg = active ? total / active : 0;
  const maxIdx = values.indexOf(max);
  summary.innerHTML = `
    <div class="hsum"><div class="hsum-label">Total</div><div class="hsum-value">${{total.toFixed(0)}}h</div><div class="hsum-hint">somatorio do periodo</div></div>
    <div class="hsum"><div class="hsum-label">Dias ativos</div><div class="hsum-value">${{active}}<span style="font-size:14px;color:var(--ink-faint);"> / ${{dates.length}}</span></div><div class="hsum-hint">${{Math.round(active/dates.length*100)}}% do periodo</div></div>
    <div class="hsum"><div class="hsum-label">Media / dia ativo</div><div class="hsum-value">${{avg.toFixed(1)}}h</div><div class="hsum-hint">intensidade tipica</div></div>
    <div class="hsum"><div class="hsum-label">Pico</div><div class="hsum-value">${{max.toFixed(1)}}h</div><div class="hsum-hint">em ${{dates[maxIdx] || '-'}}</div></div>
  `;
}})();

// ---------- TOP PROJETOS ----------
(function() {{
  const ol = document.getElementById('top-projects');
  const list = DATA.top_projects || [];
  if (list.length === 0) {{
    ol.innerHTML = '<p class="muted">Nenhum projeto com atividades ainda.</p>';
    return;
  }}
  list.forEach((p, i) => {{
    const li = document.createElement('li');
    li.className = 'proj-item';
    li.innerHTML = `
      <div class="proj-rank">${{String(i+1).padStart(2,'0')}}</div>
      <div class="proj-name">${{p.project}}</div>
      <div class="proj-count">${{p.total_activities}}<em>ativ.</em></div>
    `;
    ol.appendChild(li);
  }});
}})();

// ---------- DONUT TIPOS ----------
(function() {{
  const canvas = document.getElementById('type-donut');
  const legendEl = document.getElementById('donut-legend');
  if (typeof Chart === 'undefined') {{
    canvas.parentElement.innerHTML = '<p class="muted">Chart.js indisponivel.</p>';
    return;
  }}
  const types = DATA.type_dist || {{}};
  const labels = Object.keys(types);
  const data = labels.map(l => types[l]);
  if (labels.length === 0) {{
    canvas.parentElement.innerHTML = '<p class="muted">Sem atividades registradas.</p>';
    return;
  }}
  // Paleta editorial: tinta com ascent, degrade em sepia
  const palette = ['#1a1510','#c45a2f','#6b5d4f','#8a3c1c','#a89a85','#4a3d2f','#d4c9b8','#2e2418'];
  const total = data.reduce((a,b) => a+b, 0);

  new Chart(canvas, {{
    type: 'doughnut',
    data: {{
      labels: labels,
      datasets: [{{
        data: data,
        backgroundColor: labels.map((_,i) => palette[i % palette.length]),
        borderWidth: 3,
        borderColor: '#f5f2ea'
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: true,
      cutout: '62%',
      animation: {{ duration: 900 }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: '#1a1510',
          titleFont: {{ family: 'JetBrains Mono', size: 10 }},
          bodyFont: {{ family: 'JetBrains Mono', size: 12 }},
          padding: 10,
          cornerRadius: 0
        }}
      }}
    }}
  }});

  // Legend textual
  labels.forEach((l, i) => {{
    const pct = Math.round((data[i] / total) * 100);
    const row = document.createElement('div');
    row.innerHTML = `
      <span class="sw" style="background:${{palette[i % palette.length]}}"></span>
      <span class="name">${{l}}</span>
      <span class="val">${{data[i]}} <span style="color:var(--ink-faint);">· ${{pct}}%</span></span>
    `;
    legendEl.appendChild(row);
  }});
}})();

// ---------- OBJETIVOS ----------
(function() {{
  const el = document.getElementById('objectives');
  const objs = (DATA.objectives && DATA.objectives.objectives) || [];
  if (objs.length === 0) {{
    el.innerHTML = '<p class="muted">Nenhum objetivo estrategico registrado.</p>';
    return;
  }}
  objs.forEach(o => {{
    const ratio = o.total_projects ? (o.active_projects / o.total_projects) : 0;
    const pct = Math.round(ratio * 100);
    const card = document.createElement('div');
    card.className = 'obj-card';
    card.innerHTML = `
      <div class="obj-title">${{o.title}}</div>
      <div class="obj-meta">${{o.horizon}} · alvo <span class="accent">${{o.target_date || '-'}}</span></div>
      <div class="obj-meta" style="text-align:right;">${{o.active_projects}}/${{o.total_projects}} projetos · ${{o.activities_this_month}} ativ. no mes · <span class="accent">${{pct}}%</span></div>
      <div class="obj-progress-wrap"><div class="obj-progress"><div class="obj-progress-fill" style="width:${{pct}}%"></div></div></div>
    `;
    el.appendChild(card);
  }});
}})();

// ---------- TEMAS ----------
(function() {{
  const el = document.getElementById('themes');
  const themes = DATA.themes || [];
  if (themes.length === 0) {{
    el.innerHTML = '<p class="muted">Poucos dados para extrair temas.</p>';
    return;
  }}
  const maxFreq = Math.max(...themes.map(t => t.freq));
  themes.forEach(t => {{
    const span = document.createElement('span');
    span.className = 'theme';
    const ratio = t.freq / maxFreq;
    const size = 14 + (ratio * 22);
    span.style.fontSize = size + 'px';
    span.style.fontWeight = Math.round(400 + ratio * 400);
    // Itálicos para temas dominantes
    if (ratio > 0.66) span.style.fontStyle = 'italic';
    span.textContent = t.word;
    span.title = `"${{t.word}}" · ${{t.freq}}x em ${{t.projects.length}} projeto(s)`;
    el.appendChild(span);
  }});
}})();

// ---------- TOKENS §07 ----------
(function() {{
  const host = document.getElementById('tokens-block');
  const ws = DATA.tokens_ws || [];
  const t90 = DATA.tokens_total_90 || {{}};
  const t30 = DATA.tokens_total_30 || {{}};

  if (!ws.length) {{
    host.innerHTML = '<p class="muted">Sem transcripts do Claude Code disponiveis (~/.claude/projects/). Use o Claude Code normalmente e o consumo aparece aqui.</p>';
    return;
  }}

  // Formatador: K / M / B
  const fmt = (n) => {{
    if (!n) return '0';
    if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
    if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
    return String(n);
  }};
  const fmtFull = (n) => (n || 0).toLocaleString('pt-BR');
  const pct = (n) => Math.round((n || 0) * 100) + '%';

  // Linha de KPIs (30 dias)
  const kpiRow = document.createElement('div');
  kpiRow.className = 'tk-row';
  const hitRate30 = (t30.cache_hit_rate || 0);
  kpiRow.innerHTML = `
    <div class="tk-cell">
      <div class="tk-label">Total · 30 dias</div>
      <div class="tk-value">${{fmt(t30.total || 0)}}<span class="tk-unit">tok</span></div>
      <div class="tk-hint">${{fmtFull(t30.total || 0)}} tokens no periodo</div>
    </div>
    <div class="tk-cell">
      <div class="tk-label">Cache hit rate</div>
      <div class="tk-value accent">${{Math.round(hitRate30 * 100)}}%</div>
      <div class="tk-hint">${{fmt(t30.cache_read || 0)}} cacheados · economia real</div>
    </div>
    <div class="tk-cell">
      <div class="tk-label">Output gerado</div>
      <div class="tk-value">${{fmt(t30.output || 0)}}<span class="tk-unit">tok</span></div>
      <div class="tk-hint">${{fmtFull(t30.messages || 0)}} mensagens do assistant</div>
    </div>
    <div class="tk-cell">
      <div class="tk-label">Workspaces ativos</div>
      <div class="tk-value">${{t30.workspaces || 0}}</div>
      <div class="tk-hint">${{t30.sessions || 0}} sessoes (.jsonl) com consumo</div>
    </div>
  `;
  host.appendChild(kpiRow);

  // Legend explicativa dos tipos
  const legend = document.createElement('div');
  legend.className = 'tk-legend';
  legend.innerHTML = `
    <span><span class="chip" style="background:var(--ink)"></span>Output</span>
    <span><span class="chip" style="background:var(--accent-deep)"></span>Input novo</span>
    <span><span class="chip" style="background:rgba(196,90,47,0.55)"></span>Cache escrito</span>
    <span><span class="chip" style="background:rgba(196,90,47,0.25)"></span>Cache lido</span>
    <span style="margin-left:auto;color:var(--ink-faint)">janela: 90 dias</span>
  `;
  host.appendChild(legend);

  // Sub-header da lista
  const subHead = document.createElement('div');
  subHead.style.marginTop = '32px';
  subHead.innerHTML = '<h3 style="font-family: var(--mono); font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--ink-soft); margin-bottom: 8px;">Top workspaces por consumo · 90 dias</h3>';
  host.appendChild(subHead);

  // Lista de top workspaces
  const ol = document.createElement('ol');
  ol.className = 'tk-list';
  const max = Math.max(...ws.map(w => w.total));
  ws.slice(0, 10).forEach((w, i) => {{
    const li = document.createElement('li');
    li.className = 'tk-item';
    // Barra stacked: proporcoes dos 4 tipos dentro do TOTAL DESTE workspace
    const total = w.total || 1;
    const parts = [
      {{cls: 'seg-output', val: w.output, label: 'output'}},
      {{cls: 'seg-input', val: w.input, label: 'input novo'}},
      {{cls: 'seg-cache_creation', val: w.cache_creation, label: 'cache escrito'}},
      {{cls: 'seg-cache_read', val: w.cache_read, label: 'cache lido'}},
    ];
    const segsHtml = parts.map(p => {{
      const pp = (p.val / total) * 100;
      if (pp < 0.5) return '';
      return `<div class="${{p.cls}}" style="width:${{pp}}%" title="${{p.label}}: ${{fmtFull(p.val)}} tok (${{pp.toFixed(1)}}%)"></div>`;
    }}).join('');
    // Hint secundario: cache hit deste workspace
    const paidIn = (w.input || 0) + (w.cache_creation || 0);
    const denom = paidIn + (w.cache_read || 0);
    const hitPct = denom > 0 ? Math.round((w.cache_read / denom) * 100) : 0;
    li.innerHTML = `
      <div class="tk-rank">${{String(i+1).padStart(2,'0')}}</div>
      <div class="tk-name" title="${{w.path_hint}}">
        ${{w.short}}
        <em>${{w.sessions}} sessao(oes) · cache ${{hitPct}}%</em>
      </div>
      <div class="tk-stack" title="Composicao: ${{fmtFull(w.total)}} tok">${{segsHtml}}</div>
      <div class="tk-total">${{fmt(w.total)}}<em>tok</em></div>
      <div class="tk-msgs"><strong>${{fmtFull(w.messages)}}</strong><br>msgs</div>
    `;
    ol.appendChild(li);
  }});
  host.appendChild(ol);

  // Nota de rodape
  const note = document.createElement('p');
  note.style.cssText = 'font-family: var(--mono); font-size: 10px; color: var(--ink-faint); margin-top: 16px; letter-spacing: 0.04em;';
  note.innerHTML = `Fonte: <code style="background:var(--paper-deep);padding:1px 5px;">~/.claude/projects/</code> · workspace = raiz onde o Claude Code foi aberto`;
  host.appendChild(note);
}})();

// ---------- SHARES ----------
(function() {{
  const el = document.getElementById('shares-table');
  const shares = DATA.shares || [];
  if (shares.length === 0) {{
    el.innerHTML = '<p class="muted">Nenhum projeto compartilhado ainda. Use /compartilhar para exportar.</p>';
    return;
  }}
  const table = document.createElement('table');
  table.innerHTML = `
    <thead><tr>
      <th>Data</th><th>Projeto</th><th>Destinatario</th>
      <th style="text-align:right;">Tamanho</th><th style="text-align:right;">Arquivos</th>
    </tr></thead>
    <tbody></tbody>
  `;
  const tbody = table.querySelector('tbody');
  shares.forEach(s => {{
    const tr = document.createElement('tr');
    const size = s.size_bytes ? (s.size_bytes / 1024).toFixed(1) + ' KB' : '—';
    tr.innerHTML = `
      <td>${{(s.generated_at || '').split(' ')[0]}}</td>
      <td>${{s.project}}</td>
      <td style="color:var(--ink-soft)">${{s.destinatario || '—'}}</td>
      <td style="text-align:right;">${{size}}</td>
      <td style="text-align:right;">${{s.files_count || '—'}}</td>
    `;
    tbody.appendChild(tr);
  }});
  el.appendChild(table);
}})();
</script>
</body>
</html>
"""

# Injeta o chart_script no template (o placeholder evita conflito com {})
HTML_TEMPLATE = HTML_TEMPLATE.replace("__CHART_SCRIPT_PLACEHOLDER__", "{chart_script}")


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else None
    path = generate_dashboard(output_path=out)
    print(f"[OK] Dashboard gerado: {path}")
