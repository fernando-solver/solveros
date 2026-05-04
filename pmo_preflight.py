"""
PMO Preflight - Verifica pre-requisitos do workspace antes de /setup.

Uso pelo Claude Code (via Bash interno):
    python -c "from pmo_preflight import full_report; import json; print(json.dumps(full_report('.'), ensure_ascii=False))"

Retorna JSON estruturado com:
    {
        "ok": bool,
        "blocking": [codigos],
        "warnings": [codigos],
        "info": {...},
        "messages": [{"code", "level", "text", "link", "next_cmd"}]
    }

Mensagens sao PT-BR acolhedoras, sem stack trace, sempre com proximo passo.
"""

import os
import sys
import platform


MIN_PYTHON = (3, 10)


def check_python_version() -> dict:
    """Python 3.10+ e pre-requisito (usado por sintaxe nova em pmo_db.py)."""
    version_tuple = sys.version_info[:2]
    version_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if version_tuple < MIN_PYTHON:
        return {
            'code': 'python_version',
            'level': 'block',
            'ok': False,
            'actual': version_str,
            'required': f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}+",
            'text': (
                f"Python {version_str} e antigo demais. Preciso {MIN_PYTHON[0]}.{MIN_PYTHON[1]} ou mais novo.\n"
                "O que fazer:\n"
                "  1. Baixe a versao mais recente em: https://www.python.org/downloads/\n"
                "  2. Durante a instalacao no Windows, marque 'Add python.exe to PATH'\n"
                "  3. Feche e abra o Claude Code de novo\n"
                "  4. Me avise que esta pronto"
            ),
            'link': 'https://www.python.org/downloads/',
            'next_cmd': '/setup',
        }
    return {
        'code': 'python_version',
        'level': 'info',
        'ok': True,
        'actual': version_str,
        'required': f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}+",
    }


def check_sqlite_module() -> dict:
    """sqlite3 e stdlib — falha apenas se instalacao Python estiver quebrada."""
    try:
        import sqlite3
        return {
            'code': 'sqlite3',
            'level': 'info',
            'ok': True,
            'version': sqlite3.sqlite_version,
        }
    except ImportError:
        return {
            'code': 'sqlite3',
            'level': 'block',
            'ok': False,
            'text': (
                "Seu Python nao tem o modulo sqlite3 (muito raro). Isso sugere instalacao corrompida.\n"
                "O que fazer:\n"
                "  1. Desinstale o Python atual\n"
                "  2. Reinstale pelo site oficial: https://www.python.org/downloads/\n"
                "  3. Volte aqui e digite /setup"
            ),
            'link': 'https://www.python.org/downloads/',
            'next_cmd': '/setup',
        }


def check_optional_modules() -> dict:
    """pandas e openpyxl sao opcionais (so afetam projetos que leem planilhas)."""
    results = {'code': 'optional_modules', 'level': 'info', 'ok': True, 'has': {}, 'missing': []}
    for mod in ['pandas', 'openpyxl']:
        try:
            __import__(mod)
            results['has'][mod] = True
        except ImportError:
            results['has'][mod] = False
            results['missing'].append(mod)
    if results['missing']:
        results['level'] = 'warning'
        results['text'] = (
            f"Modulos opcionais ausentes: {', '.join(results['missing'])}. Tudo vai funcionar sem eles, "
            f"mas projetos que leem Excel vao pedir instalacao.\n"
            f"Quando precisar, instale com:\n"
            f"  pip install {' '.join(results['missing'])}"
        )
    return results


def check_write_permission(path: str) -> dict:
    """Verifica se consegue escrever no diretorio."""
    try:
        probe = os.path.join(os.path.abspath(path), '.preflight_write_test')
        with open(probe, 'w') as f:
            f.write('test')
        os.remove(probe)
        return {'code': 'write_permission', 'level': 'info', 'ok': True, 'path': os.path.abspath(path)}
    except (OSError, PermissionError) as e:
        return {
            'code': 'write_permission',
            'level': 'block',
            'ok': False,
            'path': os.path.abspath(path),
            'text': (
                f"Nao consigo escrever em {os.path.abspath(path)}.\n"
                "O que fazer:\n"
                "  1. Mova a pasta do workspace para um local com permissao (ex: Desktop)\n"
                "  2. Ou ajuste as permissoes da pasta atual\n"
                "  3. Volte aqui e digite /setup"
            ),
            'link': None,
            'next_cmd': '/setup',
        }


def check_sync_service(path: str) -> dict:
    """
    Detecta se o workspace esta dentro de OneDrive/iCloud/GoogleDrive/Dropbox.
    Sync services podem corromper o SQLite WAL journal.
    """
    abs_path = os.path.abspath(path).replace('\\', '/')
    abs_lower = abs_path.lower()

    # Padroes por OS
    patterns = {
        'OneDrive': ['/onedrive', '/onedrive - '],
        'iCloud': ['/mobile documents/com~apple~clouddocs', '/icloud drive', '/icloudrive'],
        'GoogleDrive': ['/google drive', '/googledrive', '/my drive'],
        'Dropbox': ['/dropbox'],
        'pCloud': ['/pclouddrive'],
    }

    detected = []
    for service, pats in patterns.items():
        for p in pats:
            if p in abs_lower:
                detected.append(service)
                break

    if detected:
        return {
            'code': 'sync_service',
            'level': 'warning',
            'ok': True,
            'detected': detected,
            'path': abs_path,
            'text': (
                f"Notei que este workspace esta dentro de: {', '.join(detected)}.\n"
                f"O SQLite usa modo WAL e servicos de sincronizacao podem corromper o banco.\n"
                "Sugestao forte: mova o workspace para uma pasta local (ex: Desktop ou Documentos nao-sincronizados).\n"
                "Se quiser seguir assim, tudo bem — mas fique de olho no pmo.db."
            ),
            'link': None,
            'next_cmd': None,
        }
    return {'code': 'sync_service', 'level': 'info', 'ok': True, 'detected': []}


def check_path_safety(path: str) -> dict:
    """
    Detecta caminhos que causam problema:
    - UNC paths (\\\\server\\share)
    - Caracteres nao-ASCII imprimiveis
    - Path em drive de rede
    """
    abs_path = os.path.abspath(path)
    warnings = []

    # UNC Windows
    if abs_path.startswith('\\\\') or abs_path.startswith('//'):
        warnings.append('unc')

    # Caracteres fora de ASCII imprimivel
    try:
        abs_path.encode('ascii')
        has_unicode = False
    except UnicodeEncodeError:
        has_unicode = True
        warnings.append('unicode')

    if warnings:
        texts = []
        if 'unc' in warnings:
            texts.append("este caminho parece estar em um drive de rede (UNC). SQLite WAL pode falhar ai.")
        if 'unicode' in warnings:
            texts.append("este caminho tem caracteres fora do ASCII basico. Comandos no terminal podem falhar.")
        return {
            'code': 'path_safety',
            'level': 'warning',
            'ok': True,
            'path': abs_path,
            'issues': warnings,
            'text': (
                "Detectei o seguinte no caminho do workspace:\n  - "
                + "\n  - ".join(texts)
                + "\nSugestao: use uma pasta local e com nome simples (sem acentos), ex: C:/Users/SeuNome/Desktop/workspace"
            ),
            'link': None,
            'next_cmd': None,
        }
    return {'code': 'path_safety', 'level': 'info', 'ok': True, 'path': abs_path}


def check_claude_md_present(path: str) -> dict:
    """Confirma que esta rodando no diretorio certo (tem CLAUDE.md)."""
    claude_path = os.path.join(os.path.abspath(path), 'CLAUDE.md')
    if os.path.isfile(claude_path):
        return {'code': 'claude_md', 'level': 'info', 'ok': True}
    return {
        'code': 'claude_md',
        'level': 'block',
        'ok': False,
        'text': (
            f"Nao encontrei CLAUDE.md em {os.path.abspath(path)}.\n"
            "Isso sugere que voce nao esta na pasta raiz do workspace.\n"
            "O que fazer:\n"
            "  1. Feche o Claude Code\n"
            "  2. Abra de novo dentro da pasta correta (onde estao CLAUDE.md, pmo_db.py etc)\n"
            "  3. Digite /setup"
        ),
        'link': None,
        'next_cmd': '/setup',
    }


def full_report(path: str = '.') -> dict:
    """
    Roda todos os checks e consolida em um unico JSON.
    Ordem: python -> sqlite -> claude.md -> write -> path -> sync -> optional
    """
    checks = [
        check_python_version(),
        check_sqlite_module(),
        check_claude_md_present(path),
        check_write_permission(path),
        check_path_safety(path),
        check_sync_service(path),
        check_optional_modules(),
    ]

    blocking = [c['code'] for c in checks if c.get('level') == 'block']
    warnings = [c['code'] for c in checks if c.get('level') == 'warning']
    info = {
        'platform': platform.system(),
        'python': sys.version.split()[0],
        'cwd': os.path.abspath(path),
    }
    for c in checks:
        if c['code'] == 'optional_modules':
            info['has_pandas'] = c['has'].get('pandas', False)
            info['has_openpyxl'] = c['has'].get('openpyxl', False)

    messages = [
        {k: v for k, v in c.items() if k in ('code', 'level', 'text', 'link', 'next_cmd')}
        for c in checks if c.get('text')
    ]

    return {
        'ok': len(blocking) == 0,
        'blocking': blocking,
        'warnings': warnings,
        'info': info,
        'messages': messages,
    }


if __name__ == '__main__':
    import json
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    report = full_report(target)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)
