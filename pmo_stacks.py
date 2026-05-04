"""pmo_stacks — gerencia stacks do Solverkitty.

Um stack e um pacote nomeado em stacks/<nome>/ que contem:
- _template/  estrutura de pasta de cliente que o stack cria
- agents/     subagentes (.md) que entram em .claude/agents/
- commands/   slash commands (.md) que entram em .claude/commands/
- skills/     skills (.md) que entram em skills/
- modules/    .py modulos auxiliares (opcional)
- hooks/      hooks Claude Code (opcional, core entrega o session_start)
- manifest.yaml  metadados do stack

API publica:
- lista_stacks()  ->  ['core', ...]
- stack_info(nome)
- instalar_stack(nome, dry_run=False)  copia agents/commands/skills/hooks
                                         pra raiz do workspace ativo
- desinstalar_stack(nome)               remove o que o stack adicionou
"""
import os, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
STACKS_DIR = os.path.join(ROOT, 'stacks')


def lista_stacks():
    """Retorna lista de stacks instalados em stacks/."""
    if not os.path.isdir(STACKS_DIR):
        return []
    return sorted([d for d in os.listdir(STACKS_DIR)
                   if os.path.isdir(os.path.join(STACKS_DIR, d))])


def stack_path(nome):
    """Path absoluto do stack, ou None se nao existe."""
    p = os.path.join(STACKS_DIR, nome)
    return p if os.path.isdir(p) else None


def stack_info(nome):
    """Le manifest.yaml e conta artefatos do stack."""
    base = stack_path(nome)
    if not base:
        return None
    info = {'nome': nome, 'path': base}
    for sub in ['_template', 'agents', 'commands', 'skills', 'modules', 'hooks']:
        sp = os.path.join(base, sub)
        if os.path.isdir(sp):
            info[sub] = sorted(os.listdir(sp))
        else:
            info[sub] = []
    manifest = os.path.join(base, 'manifest.yaml')
    if os.path.isfile(manifest):
        with open(manifest, encoding='utf-8') as f:
            info['manifest_raw'] = f.read()
    return info


def _copy_dir_files(src_dir, dst_dir, dry_run=False, log=None):
    """Copia todos os arquivos de src_dir pra dst_dir (cria dst se preciso)."""
    if not os.path.isdir(src_dir):
        return 0
    if not dry_run:
        os.makedirs(dst_dir, exist_ok=True)
    n = 0
    for f in os.listdir(src_dir):
        src = os.path.join(src_dir, f)
        dst = os.path.join(dst_dir, f)
        if os.path.isfile(src):
            if log is not None:
                log.append(f'  copy {os.path.relpath(src, ROOT)} -> {os.path.relpath(dst, ROOT)}')
            if not dry_run:
                shutil.copy2(src, dst)
            n += 1
        elif os.path.isdir(src):
            if log is not None:
                log.append(f'  copytree {os.path.relpath(src, ROOT)} -> {os.path.relpath(dst, ROOT)}')
            if not dry_run:
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            n += 1
    return n


def instalar_stack(nome, dry_run=False):
    """Instala stack no workspace ativo.

    Copia:
      stacks/<nome>/agents/*    -> .claude/agents/
      stacks/<nome>/commands/*  -> .claude/commands/
      stacks/<nome>/skills/*    -> skills/
      stacks/<nome>/hooks/*     -> pmo_hooks/

    NOTA: nao copia _template/ pra clientes/_template/ — pasta clientes/_template/
    foi removida na Fase A.1 e nova_pasta_cliente() ja le direto de
    stacks/<stack>/_template/ via parametro.

    NOTA: nao copia modules/*.py pra raiz — modulos ficam onde estao por
    questao de import path. Em A.3 isso vira import dinamico.

    Args:
        nome: nome do stack (deve existir em stacks/<nome>/).
        dry_run: se True, retorna lista de operacoes sem executar.

    Returns:
        dict com {'stack', 'operacoes', 'aplicado'}.
    """
    base = stack_path(nome)
    if not base:
        raise ValueError(f"Stack '{nome}' nao encontrado em {STACKS_DIR}")

    log = []
    total = 0

    pares = [
        (os.path.join(base, 'agents'),   os.path.join(ROOT, '.claude', 'agents')),
        (os.path.join(base, 'commands'), os.path.join(ROOT, '.claude', 'commands')),
        (os.path.join(base, 'skills'),   os.path.join(ROOT, 'skills')),
        (os.path.join(base, 'hooks'),    os.path.join(ROOT, 'pmo_hooks')),
    ]
    for src, dst in pares:
        total += _copy_dir_files(src, dst, dry_run=dry_run, log=log)

    return {
        'stack': nome,
        'operacoes': log,
        'arquivos': total,
        'aplicado': not dry_run,
    }


def desinstalar_stack(nome, dry_run=False):
    """Remove arquivos que o stack adicionou ao workspace.

    Compara stacks/<nome>/<sub>/<f> com .claude/<sub>/<f> (ou skills/<f>) e
    remove o de destino se existir e tiver conteudo identico ao do stack.
    Por seguranca, nao remove se foi modificado localmente.

    Returns:
        dict com {'stack', 'removidos', 'preservados', 'aplicado'}.
    """
    base = stack_path(nome)
    if not base:
        raise ValueError(f"Stack '{nome}' nao encontrado em {STACKS_DIR}")

    removidos = []
    preservados = []

    pares = [
        (os.path.join(base, 'agents'),   os.path.join(ROOT, '.claude', 'agents')),
        (os.path.join(base, 'commands'), os.path.join(ROOT, '.claude', 'commands')),
        (os.path.join(base, 'skills'),   os.path.join(ROOT, 'skills')),
    ]
    for src, dst in pares:
        if not os.path.isdir(src):
            continue
        for f in os.listdir(src):
            src_f = os.path.join(src, f)
            dst_f = os.path.join(dst, f)
            if not os.path.isfile(dst_f):
                continue
            with open(src_f, 'rb') as a, open(dst_f, 'rb') as b:
                igual = a.read() == b.read()
            if igual:
                if not dry_run:
                    os.remove(dst_f)
                removidos.append(os.path.relpath(dst_f, ROOT))
            else:
                preservados.append(os.path.relpath(dst_f, ROOT))

    return {
        'stack': nome,
        'removidos': removidos,
        'preservados': preservados,
        'aplicado': not dry_run,
    }


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    sub.add_parser('list')
    p_inst = sub.add_parser('install')
    p_inst.add_argument('stack')
    p_inst.add_argument('--dry-run', action='store_true')
    p_uninst = sub.add_parser('uninstall')
    p_uninst.add_argument('stack')
    p_uninst.add_argument('--dry-run', action='store_true')
    p_info = sub.add_parser('info')
    p_info.add_argument('stack')

    args = ap.parse_args()
    if args.cmd == 'list':
        for p in lista_stacks():
            print(p)
    elif args.cmd == 'info':
        info = stack_info(args.stack)
        if not info:
            print(f"[ERRO] stack '{args.stack}' nao encontrado")
            sys.exit(1)
        for k, v in info.items():
            if k == 'manifest_raw':
                continue
            if isinstance(v, list):
                print(f'{k}: {len(v)} item(s)')
                for it in v:
                    print(f'  - {it}')
            else:
                print(f'{k}: {v}')
    elif args.cmd == 'install':
        r = instalar_stack(args.stack, dry_run=args.dry_run)
        for op in r['operacoes']:
            print(op)
        print(f"[OK] {r['arquivos']} arquivos {'(dry-run)' if args.dry_run else 'instalados'}")
    elif args.cmd == 'uninstall':
        r = desinstalar_stack(args.stack, dry_run=args.dry_run)
        print(f"removidos: {len(r['removidos'])}, preservados (modificados): {len(r['preservados'])}")
        for f in r['removidos']:
            print(f'  - {f}')
        if r['preservados']:
            print('Arquivos modificados localmente (preservados):')
            for f in r['preservados']:
                print(f'  ! {f}')
    else:
        ap.print_help()
