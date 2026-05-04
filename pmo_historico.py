"""
PMO Historico - Writer append-only de historico.md por cliente (v0.5).

Cada cliente tem um historico.md em sua pasta. Cada acao registrada como
linha cronologica. A diferenca para o pmo.db (activities) e que historico.md
e legivel offline e sobrevive sem o banco — e a versao humana do log.

Convencao: cada entrada em uma linha
  - YYYY-MM-DD HH:MM | tipo | descricao [| arquivo: caminho]

Uso:
  from pmo_historico import append_historico
  append_historico('clienteX', 'briefing', 'Versao 4 do briefing aprovada',
                   arquivo='01_briefing/briefing_v04.md')
"""

import os
from datetime import datetime
from pmo_db import DB_PATH

ROOT = os.path.dirname(os.path.abspath(DB_PATH))
CLIENTES_DIR = os.path.join(ROOT, "clientes")

HEADER = """# Histórico — {nome}

> Append-only. Cada linha e um evento cronologico.
> Formato: `YYYY-MM-DD HH:MM | tipo | descricao [| arquivo]`
> Nao edite eventos passados. Para correcao, registre nova entrada com tipo `correcao`.

"""


def historico_path(slug, root=None):
    """Resolve caminho do historico.md do cliente."""
    base = os.path.join(root, "clientes") if root else CLIENTES_DIR
    return os.path.join(base, slug, "historico.md")


def _garantir_historico(slug, nome=None, root=None):
    """Cria historico.md com header se nao existir. Retorna path."""
    path = historico_path(slug, root=root)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(HEADER.format(nome=nome or slug))
    return path


def append_historico(slug, tipo, descricao, arquivo=None, nome=None,
                     timestamp=None, root=None):
    """Append uma entrada no historico.md do cliente.

    Args:
        slug: identificador do cliente.
        tipo: categoria curta (briefing | trafego | dados | decisao | correcao | etc.)
        descricao: texto livre do evento.
        arquivo: caminho relativo a pasta do cliente (opcional).
        nome: nome legivel (so usado se historico.md ainda nao existe).
        timestamp: datetime customizado (default: agora local).
        root: raiz alternativa (default: workspace do pmo.db).

    Returns:
        path do historico.md atualizado.
    """
    if not slug or not tipo or not descricao:
        raise ValueError("slug, tipo e descricao sao obrigatorios")
    path = _garantir_historico(slug, nome=nome, root=root)
    ts = (timestamp or datetime.now()).strftime("%Y-%m-%d %H:%M")
    desc = descricao.replace("\n", " ").replace("|", "\\|").strip()
    linha = f"- {ts} | {tipo} | {desc}"
    if arquivo:
        linha += f" | `{arquivo}`"
    with open(path, "a", encoding="utf-8") as f:
        f.write(linha + "\n")
    return path


def ler_historico(slug, limit=None, root=None):
    """Le historico.md cru. Se limit, retorna so as ultimas N linhas de evento."""
    path = historico_path(slug, root=root)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        conteudo = f.read()
    if limit is None:
        return conteudo
    eventos = [l for l in conteudo.splitlines() if l.startswith("- ")]
    return "\n".join(eventos[-limit:])


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Uso: python pmo_historico.py <slug> <tipo> <descricao> [arquivo]")
        sys.exit(1)
    slug = sys.argv[1]
    tipo = sys.argv[2]
    descricao = sys.argv[3]
    arquivo = sys.argv[4] if len(sys.argv) > 4 else None
    path = append_historico(slug, tipo, descricao, arquivo=arquivo)
    print(f"[OK] entrada anexada em {path}")
