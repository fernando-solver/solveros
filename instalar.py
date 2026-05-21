"""
Instalador guiado do Solver Filesystem.

Uso:
    python instalar.py

Ou diretamente apontando o destino:
    python instalar.py "C:/Users/SeuUsuario/Desktop/MEU_WORKSPACE"

O que faz:
1. Pergunta onde voce quer o workspace (ou aceita via argumento)
2. Copia todos os arquivos do kit para la
3. Inicializa o banco SQLite (pmo.db)
4. Mostra proximo passo: abrir Claude Code na pasta e rodar /comecar

Este script NAO faz a configuracao inicial do agente (nome, papel, categorias).
Essa parte e feita pelo proprio Claude Code via /setup, de forma conversada.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

KIT_DIR = Path(__file__).parent.resolve()

# Arquivos e pastas a copiar (relativos a este script)
ITEMS_TO_COPY = [
    'COMEÇAR-AQUI.html',
    'COMEÇAR-AQUI.txt',
    'CLAUDE.md',
    'GLOSSARIO.md',
    'DIARIO.md',
    'README.md',
    'guia-filesystem.md',
    'playbook.md',
    'pmo_db.py',
    'pmo_setup.py',
    'pmo_preflight.py',
    'pmo_share.py',       # v0.3
    'pmo_dashboard.py',   # v0.3
    '000000_pmo_consolidacao',
    'skills',
    'assets',             # v0.3
    '.claude',            # v0.3 — slash commands customizados
]


def print_advisory():
    """Aviso inicial recomendando o caminho mais facil (COMEÇAR-AQUI.html)."""
    print("=" * 72)
    print("  AVISO: Voce esta na rota tecnica (instalar.py)")
    print("=" * 72)
    print()
    print("  Se preferir uma rota mais facil, abra o arquivo")
    print("  COMEÇAR-AQUI.html no navegador e siga os 4 passos visuais.")
    print("  Zero terminal necessario.")
    print()
    print("  Voce esta aqui porque sabe o que esta fazendo? Ok, continue.")
    print("=" * 72)
    print()
    resp = input("Continuar com instalacao via terminal? [s/N]: ").strip().lower()
    if resp != 's':
        print()
        print("Sem problema. Abra COMEÇAR-AQUI.html quando quiser.")
        sys.exit(0)
    print()


def print_banner():
    print("=" * 60)
    print("  Instalador do Kit Solver Filesystem v0.3 (beta)")
    print("=" * 60)
    print()


def ask_destination():
    print("Onde voce quer instalar seu workspace?")
    print("Exemplos:")
    print("  Windows: C:/Users/SeuNome/Desktop/MEU_WORKSPACE")
    print("  Mac/Linux: ~/Desktop/MEU_WORKSPACE")
    print()
    dest = input("Caminho: ").strip()
    return dest


def validate_destination(dest_str):
    dest = Path(dest_str).expanduser().resolve()
    if dest.exists() and any(dest.iterdir()):
        print(f"\n[AVISO] A pasta {dest} ja existe e NAO esta vazia.")
        resp = input("Quer continuar mesmo assim? (os arquivos existentes serao preservados; apenas os do kit serao copiados) [s/N]: ").strip().lower()
        if resp != 's':
            print("[INFO] Instalacao cancelada.")
            sys.exit(0)
    return dest


def copy_files(dest):
    dest.mkdir(parents=True, exist_ok=True)
    for item in ITEMS_TO_COPY:
        src = KIT_DIR / item
        if not src.exists():
            print(f"[AVISO] {item} nao encontrado no kit — pulando")
            continue
        dst = dest / item
        if src.is_dir():
            if dst.exists():
                print(f"[INFO] {item}/ ja existe no destino — mesclando conteudo")
                for child in src.rglob('*'):
                    rel = child.relative_to(src)
                    target = dst / rel
                    if child.is_dir():
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if not target.exists():
                            shutil.copy2(child, target)
            else:
                shutil.copytree(src, dst)
            print(f"[OK] {item}/ copiado")
        else:
            shutil.copy2(src, dst)
            print(f"[OK] {item} copiado")


def init_db_at(dest):
    """Inicializa pmo.db na pasta de destino via subprocess."""
    print("\n[INFO] Inicializando banco SQLite (pmo.db)...")
    result = subprocess.run(
        [sys.executable, '-c', 'from pmo_db import init_db; print(init_db())'],
        cwd=str(dest),
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"[OK] Banco inicializado: {dest / 'pmo.db'}")
    else:
        print(f"[ERRO] Falhou ao inicializar banco:")
        print(result.stderr)
        print("\nVoce pode tentar manualmente:")
        print(f"  cd \"{dest}\"")
        print("  python -c \"from pmo_db import init_db; init_db()\"")


def print_next_steps(dest):
    print()
    print("=" * 60)
    print("  [OK] Instalacao concluida")
    print("=" * 60)
    print()
    print("Proximo passo:")
    print()
    print(f"  1. Abra um terminal na pasta do workspace:")
    print(f'     cd "{dest}"')
    print()
    print("  2. Inicie o Claude Code nessa pasta:")
    print("     claude")
    print()
    print("  3. Dentro do Claude Code, digite:")
    print("     /comecar")
    print()
    print("  O Claude Code vai conduzir uma conversa de 2 minutos para")
    print("  personalizar seu workspace (nome, agente, papel, categorias).")
    print()
    print("  Leitura recomendada depois do setup:")
    print(f"     - {dest / 'README.md'}")
    print(f"     - {dest / 'guia-filesystem.md'}")
    print()


def main():
    # Mostra aviso a menos que usuario ja esteja sinalizando intencao tecnica (arg ou flag)
    if len(sys.argv) == 1:
        print_advisory()

    print_banner()

    # Destino: argumento ou prompt
    if len(sys.argv) > 1:
        dest_str = sys.argv[1]
    else:
        dest_str = ask_destination()

    if not dest_str:
        print("[ERRO] Caminho vazio. Saindo.")
        sys.exit(1)

    dest = validate_destination(dest_str)
    print(f"\n[INFO] Destino: {dest}")
    print()

    copy_files(dest)
    init_db_at(dest)
    print_next_steps(dest)


if __name__ == '__main__':
    main()
