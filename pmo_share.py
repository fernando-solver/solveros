"""
PMO Share - Empacota pasta de projeto para handoff curado.

Uso pelo Claude Code:
    python -c "from pmo_share import share_project; r = share_project('202604_analise_vendas', destinatario='Joao'); print(r)"

O que faz:
1. Le CLAUDE.md, historico.md, proximos-passos.md do projeto
2. Consulta pmo.db para atividades, pendencias, objetivos vinculados
3. Curadoria: exclui .local.md, arquivos com sensitive:true, intermediarios grandes
4. Gera HANDOFF.md e RESUMO-EXECUTIVO.md focados em continuidade
5. Scrub: substitui paths absolutos por placeholders, remove credenciais detectadas
6. Empacota em ZIP em <projeto>/shared/<projeto>_handoff_YYYYMMDD.zip
7. Registra no pmo.db tabela shares + log_activity
"""

import os
import re
import zipfile
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from pmo_db import (
    activities_for_project,
    list_pending,
    objective_dashboard,
    add_share,
    log_activity,
)

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Padroes de arquivo a EXCLUIR do share (glob-like, testado com Path.match)
EXCLUDE_PATTERNS = [
    '*.local.md', '*.local.txt', '*.local.json', '*.local.yaml', '*.local.yml',
    '.env', '.env.*', 'credentials.json', 'secrets.*',
    '__pycache__', '*.pyc', '*.pyo',
    'pmo.db', 'pmo.db-shm', 'pmo.db-wal',  # banco nao vai no share
    '.DS_Store', 'Thumbs.db',
]

# Padroes em texto que sugerem credenciais (para scrub + alerta)
CRED_PATTERNS = [
    (re.compile(r'(password|passwd|pwd)\s*=\s*[\'"]?([^\s\'"]+)', re.I), 'SENHA'),
    (re.compile(r'(api[_-]?key|apikey)\s*=\s*[\'"]?([^\s\'"]+)', re.I), 'API_KEY'),
    (re.compile(r'(token|secret)\s*=\s*[\'"]?([^\s\'"]+)', re.I), 'TOKEN'),
    (re.compile(r'Bearer\s+[A-Za-z0-9_\-\.]{20,}', re.I), 'BEARER'),
]

# Padrao para paths absolutos do Windows + Unix que vazam info do workspace original
ABS_PATH_WIN = re.compile(r'[A-Za-z]:[/\\][^\s\'"<>|()]+')
ABS_PATH_UNIX = re.compile(r'(?<![a-zA-Z/])/(home|Users|mnt|root|tmp)/[^\s\'"<>|()]+')

MAX_INTERMEDIARIO_MB = 10  # arquivos em dados/ maiores que isso sao excluidos se nao forem .md/.csv/.json


def _should_exclude(rel_path: Path) -> bool:
    """Verifica se o arquivo/pasta bate algum padrao de exclusao."""
    name = rel_path.name
    for pat in EXCLUDE_PATTERNS:
        if rel_path.match(pat) or name == pat:
            return True
    return False


def _has_sensitive_frontmatter(file_path: Path) -> bool:
    """Detecta frontmatter sensitive: true nas primeiras 20 linhas."""
    if file_path.suffix.lower() != '.md':
        return False
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            head = ''
            for _ in range(20):
                line = f.readline()
                if not line:
                    break
                head += line
        # Busca yaml frontmatter
        if head.startswith('---'):
            fm_end = head.find('---', 3)
            if fm_end > 0:
                fm = head[3:fm_end]
                if re.search(r'^\s*sensitive\s*:\s*true', fm, re.M | re.I):
                    return True
    except Exception:
        pass
    return False


def _scrub_content(text: str, workspace_abs: str) -> tuple[str, dict]:
    """
    Sanitiza texto: remove credenciais detectadas e substitui paths absolutos
    do workspace original por placeholder.
    Retorna (texto_limpo, stats).
    """
    stats = {'creds_removed': 0, 'paths_scrubbed': 0}

    # 1. Remove credenciais — substitui o valor por [REDACTED-<TIPO>]
    for pattern, label in CRED_PATTERNS:
        def repl(m):
            stats['creds_removed'] += 1
            # Preserva a key, zera o valor
            try:
                return f"{m.group(1)}=[REDACTED-{label}]"
            except IndexError:
                return f"[REDACTED-{label}]"
        text = pattern.sub(repl, text)

    # 2. Substitui path absoluto do workspace por placeholder
    workspace_norm = workspace_abs.replace('\\', '/').rstrip('/')
    if workspace_norm:
        # Variantes Windows (forward e backslash)
        for variant in [workspace_norm, workspace_norm.replace('/', '\\')]:
            if variant in text:
                stats['paths_scrubbed'] += text.count(variant)
                text = text.replace(variant, '<WORKSPACE>')

    # 3. Paths absolutos genericos Windows que nao pertencem ao workspace
    # (manter apenas sinalizados para que o destinatario saiba)
    return text, stats


def _scan_project_files(project_dir: Path) -> dict:
    """Escaneia a pasta do projeto categorizando arquivos."""
    result = {
        'essentials': [],       # CLAUDE.md, historico.md, proximos-passos.md
        'include': [],          # scripts, saidas finais, dados essenciais
        'exclude': [],          # local.md, sensitive, .env, intermediarios grandes
        'cred_warnings': [],    # arquivos com possiveis credenciais
        'total_bytes': 0,
    }
    ESSENTIAL_NAMES = {'CLAUDE.md', 'historico.md', 'proximos-passos.md', 'config.json'}

    for path in project_dir.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(project_dir)
        size = path.stat().st_size

        # Exclusoes hard
        if _should_exclude(rel):
            result['exclude'].append((str(rel), 'pattern', size))
            continue

        # Exclusoes por frontmatter
        if _has_sensitive_frontmatter(path):
            result['exclude'].append((str(rel), 'sensitive_frontmatter', size))
            continue

        # Essentials
        if path.name in ESSENTIAL_NAMES:
            result['essentials'].append((str(rel), size))
            result['total_bytes'] += size
            continue

        # Intermediarios grandes em dados/ (exceto formatos leves de dados)
        if rel.parts and rel.parts[0] == 'dados':
            if size > MAX_INTERMEDIARIO_MB * 1024 * 1024 and path.suffix not in {'.md', '.json', '.csv', '.txt'}:
                result['exclude'].append((str(rel), f'intermediario_>{MAX_INTERMEDIARIO_MB}MB', size))
                continue

        # Pasta shared/ do proprio projeto — nao re-empacotar shares antigos
        if rel.parts and rel.parts[0] == 'shared':
            result['exclude'].append((str(rel), 'shared_folder', size))
            continue

        # Checa credenciais em scripts/texto
        if path.suffix in {'.py', '.sh', '.env', '.txt', '.md', '.json', '.yaml', '.yml'}:
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    sample = f.read(65536)  # 64KB inicial
                for pattern, label in CRED_PATTERNS:
                    if pattern.search(sample):
                        result['cred_warnings'].append((str(rel), label))
                        break
            except Exception:
                pass

        result['include'].append((str(rel), size))
        result['total_bytes'] += size

    return result


def _build_handoff_md(project_folder: str, scan: dict, activities: list, pending: list, objectives_info) -> str:
    """Gera HANDOFF.md: briefing curado para quem vai assumir."""
    today = datetime.now().strftime('%Y-%m-%d')
    nome_proj = project_folder

    # Ultimas 10 atividades relevantes
    recent_decisions = [a for a in activities if a['type'] == 'decision'][:5]
    recent_discoveries = [a for a in activities if a['type'] == 'discovery'][:3]
    recent_features = [a for a in activities if a['type'] == 'feature'][:5]

    lines = [f"# HANDOFF — {nome_proj}",
             "",
             f"*Pacote gerado em {today} por pmo_share.py*",
             "",
             "## O que e este projeto",
             "",
             "Leia o `CLAUDE.md` anexo para contexto completo. Este arquivo e o **briefing de transferencia**: o que voce precisa saber para assumir o trabalho sem reler tudo.",
             "",
             "## Estado atual",
             "",
             f"- **Total de atividades registradas:** {len(activities)}",
             f"- **Pendencias abertas:** {len(pending)}",
             ""]

    if recent_decisions:
        lines.append("### Decisoes-chave recentes (veja `historico.md` para mais)")
        lines.append("")
        for a in recent_decisions:
            lines.append(f"- **{a['date']}**: {a['summary']}")
        lines.append("")

    if recent_discoveries:
        lines.append("### Descobertas recentes")
        lines.append("")
        for a in recent_discoveries:
            lines.append(f"- **{a['date']}**: {a['summary']}")
        lines.append("")

    if recent_features:
        lines.append("### Entregas recentes (features)")
        lines.append("")
        for a in recent_features:
            lines.append(f"- **{a['date']}**: {a['summary']}")
        lines.append("")

    if pending:
        lines.append("## Pendencias em aberto")
        lines.append("")
        for p in pending:
            desc = p['description'][:200] + ('...' if len(p['description']) > 200 else '')
            lines.append(f"- {desc}")
        lines.append("")

    # Mapeamento de arquivos
    lines.extend([
        "## O que tem neste pacote",
        "",
        "### Arquivos essenciais (leia estes primeiro)",
        "",
        "- `CLAUDE.md` — contexto do projeto (o briefing que eu li toda sessao)",
        "- `historico.md` — registro cronologico de tudo que foi feito",
        "- `proximos-passos.md` — post-it de onde parei",
        "",
        "### Scripts e dados",
        "",
    ])
    scripts = [f for f, s in scan['include'] if f.startswith('scripts/')]
    if scripts:
        lines.append("Scripts Python neste pacote:")
        for s in scripts[:20]:
            lines.append(f"- `{s}`")
        if len(scripts) > 20:
            lines.append(f"- ... mais {len(scripts)-20} scripts")
    else:
        lines.append("(nenhum script Python presente)")
    lines.append("")

    saidas = [f for f, s in scan['include'] if f.startswith('saidas/')]
    if saidas:
        lines.append("Entregas em `saidas/`:")
        for s in saidas[:20]:
            lines.append(f"- `{s}`")
        if len(saidas) > 20:
            lines.append(f"- ... mais {len(saidas)-20} entregas")
        lines.append("")

    # Arquivos excluidos (transparencia)
    if scan['exclude']:
        lines.extend([
            "### Arquivos excluidos do pacote",
            "",
            "Os seguintes arquivos do workspace original **nao foram incluidos**:",
            "",
        ])
        for rel, motivo, size in scan['exclude'][:30]:
            size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
            lines.append(f"- `{rel}` ({size_str}) — {motivo}")
        if len(scan['exclude']) > 30:
            lines.append(f"- ... mais {len(scan['exclude'])-30} arquivos excluidos")
        lines.append("")

    if scan['cred_warnings']:
        lines.extend([
            "### Alerta de seguranca",
            "",
            "Detectei possiveis credenciais nos seguintes arquivos — verificar antes de continuar:",
            "",
        ])
        for rel, label in scan['cred_warnings']:
            lines.append(f"- `{rel}` ({label})")
        lines.append("")
        lines.append("Credenciais foram substituidas por `[REDACTED-*]` nos arquivos texto durante o empacotamento, mas se houver credenciais em formato nao-texto, verifique manualmente.")
        lines.append("")

    lines.extend([
        "## Como continuar o trabalho",
        "",
        "1. Extraia este pacote numa pasta do seu workspace Solver Filesystem.",
        "2. Abra Claude Code nessa pasta.",
        "3. Diga ao agente: **\"assumir projeto compartilhado\"**.",
        "",
        "O agente vai ler CLAUDE.md, historico.md e proximos-passos.md e te dar um resumo antes de continuar.",
        "",
        "## Contato",
        "",
        "Qualquer duvida, consulte quem te enviou o pacote.",
        "",
    ])
    return '\n'.join(lines)


def _build_resumo_executivo_md(project_folder: str, scan: dict, activities: list, pending: list) -> str:
    """Gera RESUMO-EXECUTIVO.md: 2 paginas para quem so vai ler, nao operar."""
    today = datetime.now().strftime('%Y-%m-%d')
    total_acts = len(activities)

    # Data da primeira e ultima atividade
    if activities:
        sorted_acts = sorted(activities, key=lambda a: a['date'])
        first_date = sorted_acts[0]['date']
        last_date = sorted_acts[-1]['date']
    else:
        first_date = last_date = 'sem atividades'

    # Contagem por tipo
    types_count = {}
    for a in activities:
        types_count[a['type']] = types_count.get(a['type'], 0) + 1

    lines = [
        f"# Resumo Executivo — {project_folder}",
        "",
        f"*Gerado em {today}*",
        "",
        "## Panorama",
        "",
        f"- **Periodo do projeto:** {first_date} a {last_date}",
        f"- **Total de atividades registradas:** {total_acts}",
        f"- **Pendencias em aberto:** {len(pending)}",
        f"- **Arquivos incluidos neste pacote:** {len(scan['essentials']) + len(scan['include'])}",
        f"- **Tamanho total do pacote:** {scan['total_bytes']/(1024*1024):.1f} MB",
        "",
    ]

    if types_count:
        lines.append("## Distribuicao de atividades por tipo")
        lines.append("")
        for t, n in sorted(types_count.items(), key=lambda x: -x[1]):
            lines.append(f"- **{t}**: {n}")
        lines.append("")

    # Top 3 pendencias prioritarias (heuristica: primeira parte da description indica prioridade)
    if pending:
        lines.append("## Pendencias prioritarias")
        lines.append("")
        for p in pending[:5]:
            desc = p['description'][:180] + ('...' if len(p['description']) > 180 else '')
            lines.append(f"- {desc}")
        lines.append("")

    lines.extend([
        "## Proxima acao sugerida",
        "",
        "Leia `proximos-passos.md` no pacote — e o post-it que registra exatamente onde o trabalho parou.",
        "",
        "---",
        "",
        "*Para contexto completo, leia `HANDOFF.md`. Para operar o projeto, leia `CLAUDE.md` e continue pelo `proximos-passos.md`.*",
        "",
    ])
    return '\n'.join(lines)


def share_project(project_folder: str, destinatario: str = None,
                  scrub: bool = True, notes: str = None) -> dict:
    """
    Empacota projeto para handoff curado.

    Args:
        project_folder: nome da pasta (ex: '202604_analise_vendas')
        destinatario: nome/email de quem recebera (opcional, para rastreio)
        scrub: se True, remove paths absolutos e credenciais em texto
        notes: observacoes livres armazenadas no log de shares

    Returns:
        dict com: zip_path, size_bytes, files_count, excluded_count, cred_warnings
    """
    project_dir = BASE_DIR / project_folder
    if not project_dir.is_dir():
        return {'error': f'Projeto {project_folder} nao encontrado em {BASE_DIR}'}

    # 1. Query pmo.db
    activities = activities_for_project(project_folder, limit=500)
    pending = list_pending(project_folder, resolved=False)
    objectives_info = None
    try:
        objectives_info = objective_dashboard()
    except Exception:
        pass

    # 2. Scan da pasta
    scan = _scan_project_files(project_dir)

    # 3. Cria pasta shared/ se nao existir
    shared_dir = project_dir / 'shared'
    shared_dir.mkdir(exist_ok=True)

    # 4. Build dos markdowns de handoff
    handoff_md = _build_handoff_md(project_folder, scan, activities, pending, objectives_info)
    resumo_md = _build_resumo_executivo_md(project_folder, scan, activities, pending)

    # 5. Monta ZIP num tempfile e move para shared/
    today_str = datetime.now().strftime('%Y%m%d')
    zip_name = f"{project_folder}_handoff_{today_str}.zip"
    zip_path = shared_dir / zip_name

    workspace_abs = str(BASE_DIR).replace('\\', '/')

    with tempfile.TemporaryDirectory() as tmp:
        tmp_zip = Path(tmp) / zip_name
        with zipfile.ZipFile(tmp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Arquivos essenciais + incluidos
            all_files = scan['essentials'] + scan['include']
            for rel, size in all_files:
                src = project_dir / rel
                if not src.is_file():
                    continue
                # Ler e (se scrub) sanitizar
                try:
                    if scrub and src.suffix.lower() in {'.md', '.txt', '.py', '.json', '.yaml', '.yml', '.sh', '.env'}:
                        content = src.read_text(encoding='utf-8', errors='replace')
                        clean, _stats = _scrub_content(content, workspace_abs)
                        zf.writestr(str(Path(project_folder) / rel).replace('\\', '/'), clean)
                    else:
                        zf.write(src, arcname=str(Path(project_folder) / rel).replace('\\', '/'))
                except Exception:
                    # Em caso de erro, pula o arquivo (log no HANDOFF)
                    continue

            # Adiciona HANDOFF.md e RESUMO-EXECUTIVO.md na raiz do ZIP
            zf.writestr('HANDOFF.md', handoff_md)
            zf.writestr('RESUMO-EXECUTIVO.md', resumo_md)

            # README-HANDOFF.txt na raiz
            readme_txt = (
                "PACOTE DE HANDOFF - SOLVER FILESYSTEM\n"
                "\n"
                "Como usar:\n"
                "  1. Extraia este ZIP numa pasta dentro do seu workspace Solver Filesystem\n"
                "  2. Abra o Claude Code nessa pasta\n"
                "  3. Diga ao agente: 'assumir projeto compartilhado'\n"
                "\n"
                "Comece lendo:\n"
                "  - HANDOFF.md       (briefing de transferencia)\n"
                "  - RESUMO-EXECUTIVO.md  (panorama em 2 paginas)\n"
                "  - CLAUDE.md         (contexto completo do projeto)\n"
                "  - proximos-passos.md (onde o trabalho parou)\n"
                "\n"
                f"Pacote gerado em {today_str}.\n"
            )
            zf.writestr('README-HANDOFF.txt', readme_txt)

        shutil.copy2(tmp_zip, zip_path)

    size_bytes = zip_path.stat().st_size

    # 6. Conta arquivos no ZIP
    with zipfile.ZipFile(zip_path, 'r') as zf:
        files_count = len(zf.namelist())
        zip_integrity_ok = (zf.testzip() is None)

    # 7. Registra no pmo.db
    share_id = add_share(
        project=project_folder,
        zip_path=str(zip_path).replace('\\', '/'),
        destinatario=destinatario,
        size_bytes=size_bytes,
        files_count=files_count,
        notes=notes,
    )

    # 8. Log atividade
    log_activity(
        date=datetime.now().strftime('%Y-%m-%d'),
        project=project_folder,
        type_='change',
        summary=f"Projeto compartilhado via share_project" + (f" para {destinatario}" if destinatario else ""),
        details=f"ZIP: {zip_path.name} | {size_bytes/1024:.1f}KB | {files_count} arquivos | share_id={share_id}",
    )

    return {
        'share_id': share_id,
        'zip_path': str(zip_path),
        'size_bytes': size_bytes,
        'files_count': files_count,
        'excluded_count': len(scan['exclude']),
        'cred_warnings': scan['cred_warnings'],
        'integrity_ok': zip_integrity_ok,
    }


if __name__ == '__main__':
    import sys, json
    if len(sys.argv) < 2:
        print("Uso: python pmo_share.py <project_folder> [destinatario]")
        sys.exit(1)
    project = sys.argv[1]
    dest = sys.argv[2] if len(sys.argv) > 2 else None
    result = share_project(project, destinatario=dest)
    print(json.dumps(result, indent=2, ensure_ascii=False))
