"""
PMO Index - Gerador de INDEX.md por cliente (v0.5).

Renderiza um INDEX.md legivel para humanos a partir das tabelas v0.5:
  - clientes (identidade)
  - cliente_index (caminhos canonicos)
  - cliente_objetivos (metas e progresso)
  - auditoria_entropia (saude da pasta)

INDEX.md e a fonte canonica que responde "cadê o relatorio de maio?".
Atualizado idealmente por hook PostToolUse, ou manualmente via
  python -c "from pmo_index import gerar_index; gerar_index('slug-cliente')"

Convencao: pasta do cliente = clientes/<slug>/ relativa ao DB_PATH.
"""

import os
from datetime import datetime
from pmo_db import (
    cliente_get,
    index_resolve_canonical,
    objetivo_progress,
    auditoria_open_issues,
    DB_PATH,
)

ROOT = os.path.dirname(os.path.abspath(DB_PATH))
CLIENTES_DIR = os.path.join(ROOT, "clientes")


def cliente_pasta(slug, root=None):
    """Resolve caminho da pasta do cliente: clientes/<slug>/."""
    base = os.path.join(root, "clientes") if root else CLIENTES_DIR
    return os.path.join(base, slug)


def _fmt_brl(v):
    if v is None:
        return "—"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_num(v, casas=2):
    if v is None:
        return "—"
    return f"{v:.{casas}f}"


def _fmt_pct(v):
    if v is None:
        return "—"
    return f"{v*100:.0f}%"


def _formata_valor_objetivo(tipo, valor):
    """Formata valor de objetivo conforme o tipo (BRL, ratio, integer)."""
    if valor is None:
        return "—"
    if tipo in ("faturamento_mensal", "cac", "aov", "ltv"):
        return _fmt_brl(valor)
    if tipo == "roas":
        return f"{valor:.2f}x"
    if tipo in ("recompra", "nps"):
        return _fmt_num(valor, casas=1)
    return str(valor)


def render_canonicos(canonicos):
    """Renderiza secao de canonicos."""
    if not canonicos:
        return "_Nenhum canônico declarado ainda._\n"
    out = []
    for tipo, info in sorted(canonicos.items()):
        caminho = info["caminho"]
        atualizado = info["atualizado_em"][:10] if info.get("atualizado_em") else "—"
        out.append(f"- **{tipo}** → [`{caminho}`]({caminho}) _(atualizado em {atualizado})_")
    return "\n".join(out) + "\n"


def render_objetivos(objetivos):
    """Renderiza tabela de objetivos com progresso."""
    if not objetivos:
        return "_Nenhum objetivo definido. Use `/onboarding-cliente` ou `objetivo_add()`._\n"
    out = ["| Tipo | Alvo | Atual | Progresso | Horizonte |",
           "|---|---|---|---|---|"]
    for o in objetivos:
        tipo = o["tipo"]
        alvo = _formata_valor_objetivo(tipo, o.get("valor_alvo"))
        atual = _formata_valor_objetivo(tipo, o.get("valor_atual"))
        pct = _fmt_pct(o.get("pct"))
        horiz = o.get("horizonte") or "—"
        out.append(f"| {tipo} | {alvo} | {atual} | {pct} | {horiz} |")
    return "\n".join(out) + "\n"


def render_saude(issues):
    """Renderiza secao de saude da pasta (auditoria_entropia)."""
    if not issues:
        return "✅ **0 problemas abertos.** Pasta limpa.\n"
    contagem = {}
    for i in issues:
        s = i.get("severidade") or "media"
        contagem[s] = contagem.get(s, 0) + 1
    resumo = ", ".join(f"{n} {s}" for s, n in sorted(contagem.items()))
    out = [f"⚠️ **{len(issues)} problemas detectados** ({resumo}).",
           "",
           "| Severidade | Tipo | Descrição | Caminho |",
           "|---|---|---|---|"]
    for i in issues:
        sev = i.get("severidade") or "media"
        tipo = i.get("tipo_problema") or "—"
        desc = (i.get("descricao") or "—").replace("|", "\\|")
        caminho = i.get("caminho_envolvido") or "—"
        out.append(f"| {sev} | {tipo} | {desc} | `{caminho}` |")
    out.append("")
    out.append("Reveja os problemas listados acima e resolva-os manualmente ou via skill apropriada.")
    return "\n".join(out) + "\n"


def render_index_md(cliente, canonicos, objetivos, issues):
    """Renderiza o INDEX.md completo a partir dos dados ja consultados."""
    nome = cliente.get("nome") or cliente.get("slug")
    slug = cliente.get("slug")
    segmento = cliente.get("segmento") or "—"
    status = cliente.get("status") or "ativo"
    mrr = _fmt_brl(cliente.get("mrr"))
    ticket = _fmt_brl(cliente.get("ticket_medio"))
    custo_agencia = _fmt_brl(cliente.get("agencia_atual_custo_brl"))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    md = []
    md.append(f"# INDEX — {nome}")
    md.append("")
    md.append(f"> Auto-gerado por `pmo_index`. Última atualização: {ts}")
    md.append("> Fonte canônica de **onde está o quê** nesta pasta. Não edite manualmente.")
    md.append("")
    md.append("## Identidade")
    md.append("")
    md.append(f"- **Slug:** `{slug}`")
    md.append(f"- **Segmento:** {segmento}")
    md.append(f"- **Status:** {status}")
    md.append(f"- **Ticket médio:** {ticket}")
    md.append(f"- **MRR:** {mrr}")
    md.append(f"- **Custo de servico terceiro:** {custo_agencia}")
    md.append("")
    md.append("## Canônicos")
    md.append("")
    md.append(render_canonicos(canonicos))
    md.append("## Objetivos")
    md.append("")
    md.append(render_objetivos(objetivos))
    md.append("## Saúde da pasta")
    md.append("")
    md.append(render_saude(issues))
    return "\n".join(md)


def gerar_index(slug, pasta=None, escrever=True):
    """Gera INDEX.md para um cliente. Retorna o texto markdown.
    Se escrever=True, persiste em <pasta>/INDEX.md (cria pasta se nao existe)."""
    cliente = cliente_get(slug)
    if not cliente:
        raise ValueError(f"Cliente '{slug}' nao encontrado em pmo.db")

    cid = cliente["id"]
    canonicos = index_resolve_canonical(cid)
    objetivos = objetivo_progress(cid)
    issues = auditoria_open_issues(cliente_id=cid)

    md = render_index_md(cliente, canonicos, objetivos, issues)

    if escrever:
        target_dir = pasta or cliente_pasta(slug)
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, "INDEX.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        return md, path

    return md


if __name__ == "__main__":
    import sys
    slug = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug:
        print("Uso: python pmo_index.py <slug-cliente>")
        sys.exit(1)
    try:
        md, path = gerar_index(slug)
        print(f"[OK] INDEX.md gerado em {path}")
    except ValueError as e:
        print(f"[ERRO] {e}")
        sys.exit(1)
