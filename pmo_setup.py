"""
PMO Setup - Funcoes para criar pastas de projeto padronizadas.

Estrutura de agente (agente):
    YYYYMM_categoria_nome/
    ├── CLAUDE.md           # Missao, escopo, regras, inputs/outputs
    ├── historico.md        # Registro cronologico
    ├── config.json         # Parametros (horario, frequencia, flags)
    ├── 01_input/
    │   └── instrucoes.md   # De onde vem os dados? (fontes, formato, qualidade)
    ├── 02_output/
    │   └── instrucoes.md   # O que preciso entregar? (formato, destinatario, KPIs)
    ├── 03_analisar/
    │   └── instrucoes.md   # O que os dados me dizem? (perguntas, hipoteses)
    │   └── tarefa_NN_nome/ # Subtarefas (criadas pelo agente)
    │       ├── execute.md
    │       └── resultado.md
    ├── 04_processar/
    │   └── instrucoes.md   # Como transformo os dados na entrega? (regras, script)
    ├── dados/              # Dados intermediarios
    ├── scripts/            # Scripts Python de execucao
    └── saidas/             # Entregas finais
"""
import os
import re
import json
import shutil
from datetime import datetime
from pmo_db import init_db, upsert_project, log_activity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REGISTRO_BLOCO = """
## Registro de progresso no banco PMO (automatico)

Ao trabalhar neste projeto, registre marcos no banco central:

```python
import sys, os as _os; sys.path.insert(0, r'{workspace_root}')
from pmo_db import log_activity
log_activity('YYYY-MM-DD', '{project_name}', 'tipo', 'O que foi feito')
```

Tipos: `decision` | `bugfix` | `feature` | `discovery` | `refactor` | `config` | `analysis` | `change`

Registre ao concluir cada marco significativo. Nao espere o usuario pedir.
""".strip()

CATEGORIAS = {
    'analise': 'Analise de dados',
    'cad': 'Cadastros',
    'integ': 'Integracao',
    'mkt': 'Marketing',
    'oper': 'Operacional',
    'pmo': 'Gestao e relatorios gerenciais',
    'sac': 'Atendimento',
    'scrap': 'Web scraping',
}


def setup_workspace(nome_agente, papel_agente, nome_usuario, categorias_custom=None):
    """
    Configura o workspace pela primeira vez: preenche CLAUDE.md, inicializa banco,
    e valida a instalacao.

    Args:
        nome_agente: nome do agente escolhido pelo usuario
        papel_agente: papel em uma frase (ex: 'gestor de BI do financeiro')
        nome_usuario: nome do humano parceiro (ex: 'Maria Silva')
        categorias_custom: dict opcional de categorias (ex: {'contas': 'Contas a pagar/receber'})

    Returns:
        True se configuracao bem-sucedida
    """
    init_db()

    claude_path = os.path.join(BASE_DIR, 'CLAUDE.md')
    if not os.path.isfile(claude_path):
        print("[ERRO] CLAUDE.md nao encontrado na raiz do workspace")
        return False

    with open(claude_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Preenche identidade
    conteudo = conteudo.replace('[PREENCHER - nome do agente]', nome_agente)
    conteudo = conteudo.replace('[PREENCHER - papel do agente]', papel_agente)
    conteudo = conteudo.replace('[PREENCHER - nome do usuario]', nome_usuario)

    # Atualiza categorias se fornecidas
    if categorias_custom:
        # Reconstroi tabela de categorias
        linhas_cat = []
        for sigla, desc in categorias_custom.items():
            linhas_cat.append(f'| `{sigla}` | {desc} |')
        nova_tabela = '| Sigla | Categoria |\n|-------|-----------|' + '\n' + '\n'.join(linhas_cat)

        # Substitui tabela existente
        import re
        conteudo = re.sub(
            r'\| Sigla \| Categoria \|\n\|-------\|-----------\|[\s\S]*?(?=\n\n)',
            nova_tabela,
            conteudo
        )

        # Atualiza CATEGORIAS no modulo para nova_pasta funcionar
        global CATEGORIAS
        CATEGORIAS = categorias_custom

    with open(claude_path, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    # Atualiza CLAUDE.md da pasta PMO
    pmo_claude = os.path.join(BASE_DIR, '000000_pmo_consolidacao', 'CLAUDE.md')
    if os.path.isfile(pmo_claude):
        with open(pmo_claude, 'r', encoding='utf-8') as f:
            pmo_conteudo = f.read()
        pmo_conteudo = pmo_conteudo.replace('[PREENCHER - responsavel]', nome_agente)
        with open(pmo_claude, 'w', encoding='utf-8') as f:
            f.write(pmo_conteudo)

    print(f"[OK] Workspace configurado")
    print(f"[OK] Agente: {nome_agente}")
    print(f"[OK] Papel: {papel_agente}")
    print(f"[OK] Parceiro humano: {nome_usuario}")
    if categorias_custom:
        print(f"[OK] Categorias personalizadas: {', '.join(categorias_custom.keys())}")
    print(f"[OK] Banco SQLite inicializado")
    print(f"[OK] Pronto para usar. Crie seu primeiro projeto com /nova-pasta")
    return True


def _slug(texto):
    """Normaliza para slug de pasta: minusculo, hifens, sem acento/espaco."""
    import unicodedata
    t = unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii')
    t = re.sub(r'[^a-z0-9]+', '-', t.lower().strip()).strip('-')
    return t or 'sem-nome'


def nova_pasta(nome, departamento, empresa, descricao, ano_mes=None, frequencia=None, missao=None):
    """
    Cria nova pasta de projeto na estrutura: _<departamento>/<AAAAMM>_<empresa>_<nome>/

    O departamento vira a pasta de topo (prefixo '_' para subir na ordenacao).
    A empresa entra no nome do projeto. empresa e departamento sao gravados como
    campos no banco (pmo.db) para permitir cruzamentos (ex: "tudo da empresa X",
    "todas as conciliacoes do grupo") independente da arvore de pastas.

    Args:
        nome: nome do projeto (ex: 'conciliacao-bancaria')
        departamento: area funcional (ex: 'financeiro', 'credito', 'fiscal')
        empresa: empresa do grupo (ex: 'jandaia')
        descricao: descricao para o glossario
        ano_mes: AAAAMM (default: mes atual)
        frequencia: frequencia de execucao (ex: 'Mensal', 'Sob demanda')
        missao: frase curta da missao (default: usa descricao)

    Returns:
        folder_rel: caminho relativo da pasta criada (_dep/AAAAMM_empresa_nome)
    """
    init_db()

    if ano_mes is None:
        ano_mes = datetime.now().strftime('%Y%m')

    dep_slug = _slug(departamento)
    emp_slug = _slug(empresa)
    nome_slug = _slug(nome)

    dept_folder = f"_{dep_slug}"
    folder_name = f"{ano_mes}_{emp_slug}_{nome_slug}"   # nome da pasta do projeto
    folder_rel = f"{dept_folder}/{folder_name}"          # id canonico (relativo a raiz)
    folder_path = os.path.join(BASE_DIR, dept_folder, folder_name)

    # Cria pasta de departamento (topo, prefixo _) + pasta do projeto
    os.makedirs(folder_path, exist_ok=True)

    # Cria estrutura de pastas padrao
    subdirs = [
        '01_input',
        '02_output',
        '03_analisar',
        '04_processar',
        'dados',
        'scripts',
        'saidas',
        'shared',  # v0.3: destino de pacotes gerados por /compartilhar
    ]
    for subdir in subdirs:
        os.makedirs(os.path.join(folder_path, subdir), exist_ok=True)

    # Cria CLAUDE.md
    titulo = nome.replace('-', ' ').title()
    bloco_registro = REGISTRO_BLOCO.replace('{project_name}', folder_rel).replace('{workspace_root}', BASE_DIR.replace('\\', '\\\\'))
    freq_str = frequencia or 'Sob demanda'
    missao_str = missao or descricao

    claude_md = f"""# {titulo}

## Skills
Se existirem arquivos skill_*.md na raiz do workspace, leia-os antes de comecar.

## Missao
{missao_str}

## Responsavel
[PREENCHER - responsavel]

## Frequencia
{freq_str}

## Contexto
{descricao}

## Estrutura de pastas

```
{folder_name}/
├── 01_input/        # De onde vem os dados?
├── 02_output/       # O que preciso entregar? (definir destino ANTES de comecar)
├── 03_analisar/     # O que os dados me dizem? (explorar com foco)
│   └── tarefa_NN_nome/
│       ├── execute.md
│       └── resultado.md
├── 04_processar/    # Como transformo os dados na entrega?
├── dados/           # Dados intermediarios gerados
├── scripts/         # Scripts Python de execucao
└── saidas/          # Entregas finais
```

## Fluxo de trabalho

A ordem das pastas define a ordem de PENSAMENTO, nao de execucao:

1. **01_input** — Entenda o que voce tem (fontes, formato, qualidade)
2. **02_output** — Defina o que precisa entregar (formato, destinatario, KPIs)
3. **03_analisar** — Explore os dados com foco nas perguntas do output
4. **04_processar** — Construa o caminho do input ate o output

Cada pasta contem um `instrucoes.md` que guia o agente. Preencha ANTES de comecar a executar.

## Padrao de subtarefas

Dentro de `03_analisar/`, criar subtarefas como:
```
tarefa_NN_nome/
├── execute.md       # Instrucao do que investigar
└── resultado.md     # Achados (criado na execucao)
```

Numeracao sequencial define ordem de execucao.
Cada execute.md deve ser autossuficiente.

{bloco_registro}

## Comandos

### /executar
Executa o pipeline: 01_input -> 02_output (ler requisitos) -> 03_analisar -> 04_processar -> saidas/

### /fechar-projeto
Atualiza o `CLAUDE.md` e `historico.md` desta pasta com o estado atual do trabalho.
Registra atividade final no banco PMO.
"""

    with open(os.path.join(folder_path, 'CLAUDE.md'), 'w', encoding='utf-8') as f:
        f.write(claude_md)

    # Cria instrucoes.md vazios nas pastas de pipeline
    instrucoes = {
        '01_input': """# Input — De onde vem os dados?

## Fonte
- [ ] Banco de dados (qual? query?)
- [ ] Arquivo (caminho? formato? encoding?)
- [ ] API (endpoint? autenticacao?)
- [ ] Manual (quem fornece? quando?)

## Detalhes da fonte
- **Localizacao:** (caminho do arquivo, string de conexao, URL)
- **Formato:** (CSV, XLSX, JSON, SQL, outro)
- **Encoding:** (UTF-8, Latin1, CP1252)
- **Frequencia de atualizacao:** (tempo real, diario, semanal, sob demanda)
- **Volume estimado:** (N linhas, N MB)

## Qualidade conhecida
- Campos que vem vazios ou inconsistentes:
- Filtros a aplicar na origem:
- Colunas relevantes (ignorar o resto):
""",
        '02_output': """# Output — O que preciso entregar?

## Destinatario
- **Quem recebe:** (diretoria, cliente, equipe, sistema)
- **Como recebe:** (email, portal, pasta compartilhada, Asana)
- **Frequencia:** (unico, semanal, mensal, sob demanda)

## Formato
- [ ] HTML (dashboard interativo)
- [ ] XLSX (planilha formatada)
- [ ] CSV (dados para importacao)
- [ ] PDF (relatorio formal)
- [ ] Email (corpo + anexo)

## Conteudo esperado
- **KPIs / metricas principais:** (listar)
- **Comparativos:** (vs mes anterior? vs ano anterior? vs meta?)
- **Visualizacoes:** (graficos de linha, barra, tabela, mapa)

## Exemplo ou referencia
(colar aqui um print, link ou descricao de como a entrega deve parecer)

## Criterio de sucesso
(o que faz essa entrega ser considerada "boa"?)
""",
        '03_analisar': """# Analise — O que os dados me dizem?

## Perguntas a responder
1. (pergunta concreta que a entrega precisa responder)
2.
3.

## Hipoteses a testar
- (o que voce suspeita que os dados vao mostrar?)

## Segmentacoes
- (por periodo? por categoria? por cliente? por regiao?)

## Subtarefas
Criar subpastas `tarefa_NN_nome/` para cada analise:

```
tarefa_01_exploratoria/
  execute.md    <- instrucao do que investigar
  resultado.md  <- achados (criado pelo agente)
```

Numeracao sequencial define ordem de execucao.
Cada execute.md deve ser autossuficiente.
""",
        '04_processar': """# Processamento — Como transformo os dados na entrega?

## Transformacoes necessarias
- (limpeza, agregacao, joins, calculos derivados)

## Regras de negocio
- (filtros obrigatorios, exclusoes, arredondamentos, formulas)

## Validacoes
- (checagens antes de gerar a entrega: totais batem? nulos? outliers?)

## Script
- **Arquivo:** (ex: scripts/pipeline.py)
- **Parametros:** (ex: --dry-run, --data-inicio, --limit)
- **Saida:** (ex: saidas/relatorio_YYYYMMDD.html)
""",
    }
    for step_dir, content in instrucoes.items():
        instrucoes_path = os.path.join(folder_path, step_dir, 'instrucoes.md')
        with open(instrucoes_path, 'w', encoding='utf-8') as f:
            f.write(content)

    # Cria config.json
    config = {
        'nome': folder_rel,
        'missao': missao_str,
        'frequencia': freq_str,
        'ativo': True,
        'criado_em': datetime.now().strftime('%Y-%m-%d'),
        'ultima_execucao': None,
    }
    with open(os.path.join(folder_path, 'config.json'), 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # Cria historico.md
    hoje = datetime.now().strftime('%Y-%m-%d')
    historico_md = f"""# Historico - {titulo}

## {hoje}
- [feature] Projeto criado: {descricao}
"""

    with open(os.path.join(folder_path, 'historico.md'), 'w', encoding='utf-8') as f:
        f.write(historico_md)

    # Registra no banco (folder_rel = id canonico; empresa/departamento = campos queryaveis)
    upsert_project(folder_rel, descricao, 'Ativo', empresa=emp_slug, departamento=dep_slug)
    log_activity(hoje, folder_rel, 'feature', f'Projeto criado: {descricao}')

    # Adiciona ao GLOSSARIO.md
    glossario_path = os.path.join(BASE_DIR, 'GLOSSARIO.md')
    with open(glossario_path, 'r', encoding='utf-8') as f:
        glossario = f.read()

    nova_linha = f"| `{folder_rel}` | {descricao} | Ativo |"
    if folder_rel not in glossario:
        glossario = glossario.rstrip() + '\n' + nova_linha + '\n'
        with open(glossario_path, 'w', encoding='utf-8') as f:
            f.write(glossario)

    # Copia .env da raiz (caso exista — variaveis sensiveis ficam centralizadas)
    env_src = os.path.join(BASE_DIR, '.env')
    if os.path.isfile(env_src):
        shutil.copy2(env_src, os.path.join(folder_path, '.env'))
        print(f"[OK] .env copiado da raiz")

    print(f"[OK] Pasta criada: {folder_rel}")
    print(f"[OK] Estrutura padrao: 01_input/ 02_output/ 03_analisar/ 04_processar/ dados/ scripts/ saidas/")
    print(f"[OK] CLAUDE.md com missao e estrutura de agente")
    print(f"[OK] config.json inicializado")
    print(f"[OK] historico.md inicializado")
    print(f"[OK] Projeto registrado no banco (projects + activities)")
    print(f"[OK] GLOSSARIO.md atualizado")
    return folder_rel


def injetar_registro_em_projetos():
    """
    Adiciona bloco de registro no banco PMO em todos os CLAUDE.md
    que ainda nao o possuem.
    """
    atualizados = 0
    ignorados = 0

    for entry in os.listdir(BASE_DIR):
        claude_path = os.path.join(BASE_DIR, entry, 'CLAUDE.md')
        if not os.path.isfile(claude_path):
            continue

        with open(claude_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        # Ja tem a instrucao?
        if 'Registro de progresso no banco PMO' in conteudo:
            ignorados += 1
            continue

        # Determina nome do projeto para o bloco
        project_name = entry
        bloco = REGISTRO_BLOCO.replace('{project_name}', project_name)

        # Insere antes da secao "## Comandos" se existir, senao no final
        if '## Comandos' in conteudo:
            conteudo = conteudo.replace('## Comandos', f'{bloco}\n\n## Comandos')
        else:
            conteudo = conteudo.rstrip() + '\n\n' + bloco + '\n'

        with open(claude_path, 'w', encoding='utf-8') as f:
            f.write(conteudo)

        atualizados += 1

    print(f"[OK] CLAUDE.md atualizados: {atualizados}")
    print(f"[--] Ja tinham instrucao: {ignorados}")
    return atualizados


# ============================================================
# v0.5 - PASTA CLIENTE (Persona B)
# ============================================================

def nova_pasta_cliente(slug, nome=None, segmento=None, ticket_medio=None,
                      mrr=None, agencia_atual_custo_brl=None,
                      identidade_visual=None, contato=None,
                      root=None, stack='core'):
    """Cria pasta de cliente a partir do stack selecionado e registra/upserta
    cliente em pmo.db.

    Estrutura depende do stack aplicado. Core traz estrutura minima
    (inbox + saidas + _archive). Stacks especializados podem trazer mais.

    Idempotente: se cliente ja existe, garante apenas a estrutura fisica e
    sincroniza dados (nao apaga arquivos).

    Args:
        slug: kebab-case unico (ex: 'minha-empresa', 'consultorio-x').
        nome: nome legivel (default: derivado do slug).
        segmento: ex 'moda', 'beauty', 'suplemento', 'casa', 'b2b'.
        ticket_medio, mrr: valores em BRL (opcional).
        agencia_atual_custo_brl: custo mensal da agencia atual (vira baseline
            de '/economia-mes').
        identidade_visual: dict ex {'cor_primaria': '#X', 'fonte': 'Inter'}.
        contato: dict ex {'email': '...', 'whatsapp': '...'}.
        root: raiz alternativa (default: workspace).
        stack: nome do stack a aplicar. Default 'core' (estrutura minima).
            Stacks especializados podem ser instalados via /instalar-stack.

    Returns:
        dict com path, cliente_id, status ('criado' | 'atualizado'), stack.
    """
    from pmo_db import (
        cliente_get, cliente_create, cliente_update,
        DB_PATH, init_db,
    )
    from pmo_index import gerar_index
    from pmo_historico import append_historico

    # Garante schema (idempotente, custo desprezivel se ja existe).
    # Necessario pra workspace recem-clonado onde pmo.db ainda nao foi criado.
    init_db()

    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', slug):
        raise ValueError(
            f"slug invalido: '{slug}'. Use kebab-case (a-z, 0-9, -)."
        )

    nome = nome or slug.replace('-', ' ').title()
    workspace = root or os.path.dirname(os.path.abspath(DB_PATH))
    template_dir = os.path.join(workspace, 'stacks', stack, '_template')
    target_dir = os.path.join(workspace, 'clientes', slug)

    if not os.path.isdir(template_dir):
        raise FileNotFoundError(
            f"Stack '{stack}' nao encontrado em {template_dir}. "
            f"Stacks disponiveis em stacks/."
        )

    # Upsert cliente em pmo.db
    existente = cliente_get(slug)
    if existente:
        cid = existente['id']
        cliente_update(
            slug,
            nome=nome,
            segmento=segmento,
            ticket_medio=ticket_medio,
            mrr=mrr,
            agencia_atual_custo_brl=agencia_atual_custo_brl,
            identidade_visual_json=identidade_visual,
            contato_json=contato,
        )
        status = 'atualizado'
    else:
        cid = cliente_create(
            slug=slug, nome=nome, segmento=segmento,
            ticket_medio=ticket_medio, mrr=mrr,
            identidade_visual_json=identidade_visual,
            contato_json=contato,
            agencia_atual_custo_brl=agencia_atual_custo_brl,
        )
        status = 'criado'

    # Copia template (cria so o que falta)
    if not os.path.isdir(target_dir):
        shutil.copytree(template_dir, target_dir)
    else:
        # idempotencia: garante todas subpastas do template
        for nome_sub in os.listdir(template_dir):
            origem = os.path.join(template_dir, nome_sub)
            destino = os.path.join(target_dir, nome_sub)
            if os.path.isdir(origem) and not os.path.exists(destino):
                shutil.copytree(origem, destino)
            elif os.path.isfile(origem) and not os.path.exists(destino):
                shutil.copy2(origem, destino)

    # objetivos.md - substitui placeholders
    objetivos_md = os.path.join(target_dir, 'objetivos.md')
    if os.path.isfile(objetivos_md):
        with open(objetivos_md, 'r', encoding='utf-8') as f:
            txt = f.read()
        txt = txt.replace('{{NOME}}', nome).replace('{{SLUG}}', slug)
        with open(objetivos_md, 'w', encoding='utf-8') as f:
            f.write(txt)

    # historico.md - cria com header se nao existir; append do evento
    if not os.path.exists(os.path.join(target_dir, 'historico.md')):
        # historico_path resolve via clientes/<slug>/, entao usamos root explicito
        append_historico(
            slug, 'setup',
            f'Pasta criada/sincronizada via nova_pasta_cliente ({status})',
            nome=nome, root=workspace,
        )
    else:
        append_historico(
            slug, 'setup',
            f'Pasta sincronizada via nova_pasta_cliente ({status})',
            root=workspace,
        )

    # INDEX.md - gera com dados atuais do banco
    gerar_index(slug, pasta=target_dir, escrever=True)

    # Registra atividade no pmo.db
    today = datetime.now().strftime('%Y-%m-%d')
    log_activity(
        date=today,
        project=f'cliente:{slug}',
        type_='config',
        summary=f'nova_pasta_cliente: {slug} ({status})',
        details=(
            f'nome={nome} segmento={segmento} mrr={mrr} '
            f'custo_agencia={agencia_atual_custo_brl}'
        ),
    )

    print(f"[OK] Cliente {status}: {slug}")
    print(f"     id={cid}  pasta={target_dir}")
    return {'path': target_dir, 'cliente_id': cid, 'status': status, 'stack': stack}


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'injetar':
        injetar_registro_em_projetos()
    elif len(sys.argv) > 1 and sys.argv[1] == 'cliente':
        if len(sys.argv) < 3:
            print("Uso: python pmo_setup.py cliente <slug> [nome]")
            sys.exit(1)
        slug = sys.argv[2]
        nome = sys.argv[3] if len(sys.argv) > 3 else None
        nova_pasta_cliente(slug, nome=nome)
    else:
        print("Uso:")
        print("  python pmo_setup.py injetar                    # Adiciona bloco em CLAUDE.md")
        print("  python pmo_setup.py cliente <slug> [nome]      # Cria pasta de cliente (v0.5)")
        print("  python -c \"from pmo_setup import nova_pasta; nova_pasta('nome-projeto', 'departamento', 'empresa', 'descricao')\"")
