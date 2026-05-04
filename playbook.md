# Framework de Gestao por Filesystem

## O que e

Sistema de gestao onde o Claude Code navega pastas de um workspace e encontra contexto automaticamente. Cada pasta e um projeto independente contendo:

- **CLAUDE.md** — manual/briefing do projeto (o que e, como funciona, regras)
- **historico.md** — diario cronologico de tudo que foi feito
- **proximos-passos.md** — lista de retomada para a proxima sessao

Um banco SQLite centralizado (pmo.db) registra sessoes, atividades e pendencias. Scripts Python (pmo_db.py, pmo_setup.py) automatizam criacao de projetos e registro de progresso.

O resultado: qualquer sessao do Claude Code comeca com contexto completo, sem depender de memoria do usuario.

---

## /setup — Instalacao do framework

INSTRUCOES PARA CLAUDE CODE: execute cada passo sequencialmente. Pare e reporte erros.

### Passo 1: Criar pasta raiz do workspace

```bash
mkdir -p "C:/Users/USUARIO/Desktop/MEUWORKSPACE"
```

Substitua USUARIO e MEUWORKSPACE pelos valores reais informados pelo usuario.

### Passo 2: Copiar arquivos base para a raiz

Copie estes 3 arquivos para a raiz do workspace:

| Arquivo | Origem | Descricao |
|---------|--------|-----------|
| `pmo_db.py` | Fornecido com o framework | Modulo SQLite de acesso ao banco |
| `pmo_setup.py` | Fornecido com o framework | Gerador automatico de pastas de projeto |
| `CLAUDE.md` | Baseado em `CLAUDE_TEMPLATE.md` | Arquivo raiz de instrucoes — personalizar |

Os arquivos acompanham este playbook. Se estiverem em outra pasta, pergunte ao usuario onde estao.

### Passo 3: Personalizar CLAUDE.md

Abra o `CLAUDE_TEMPLATE.md` e copie como `CLAUDE.md` na raiz. Edite as secoes marcadas com `[PREENCHER]`:

- Identidade (nome do agente, papel, nome do usuario)
- Tabela de categorias de pasta (conforme departamento)
- Stack tecnica

### Passo 4: Inicializar banco SQLite

```bash
cd "CAMINHO_DO_WORKSPACE"
python -c "from pmo_db import init_db; init_db()"
```

Isso cria o arquivo `pmo.db` com as tabelas: sessions, activities, pending, projects, objectives.

### Passo 5: Criar GLOSSARIO.md

Crie o arquivo `GLOSSARIO.md` na raiz com este conteudo:

```markdown
# Glossario de Projetos

| Pasta | Categoria | Descricao | Status |
|-------|-----------|-----------|--------|
```

### Passo 6: Criar DIARIO.md

Crie o arquivo `DIARIO.md` na raiz com este conteudo:

```markdown
# Diario de Atividades

---
```

### Passo 7: Criar primeiro projeto de teste

```bash
cd "CAMINHO_DO_WORKSPACE"
python -c "from pmo_setup import nova_pasta; nova_pasta('meu-projeto', 'analise', 'Meu primeiro projeto de teste')"
```

### Passo 8: Validar a instalacao

Verifique que:

1. Pasta `YYYYMM_analise_meu-projeto/` foi criada (YYYYMM = ano e mes atual)
2. Dentro da pasta existe: `CLAUDE.md`, `historico.md`
3. `GLOSSARIO.md` contem uma linha com o novo projeto
4. `pmo.db` existe na raiz e tem tabelas populadas

```bash
python -c "from pmo_db import project_stats; print(project_stats())"
```

Se retornar dados sem erro, a instalacao esta completa.

---

## Anatomia de um projeto

### Convencao de nome

Formato obrigatorio: `YYYYMM_categoria_nome-projeto`

- YYYYMM = ano e mes de criacao (ex: 202604)
- categoria = sigla do departamento (ver tabela abaixo)
- nome-projeto = descricao curta com hifens, sempre minusculo

Exemplo: `202604_analise_vendas-por-regiao`

Excecao: a pasta PMO consolidada usa prefixo `000000` para ficar sempre no topo da listagem alfabetica.

### Categorias por departamento

As categorias sao personalizaveis. Exemplos por area:

**Ecommerce:**

| Sigla | Categoria |
|-------|-----------|
| `analise` | Analise de dados |
| `cad` | Cadastros |
| `integ` | Integracao |
| `mkt` | Marketing |
| `oper` | Operacional |
| `pmo` | Gestao e relatorios gerenciais |
| `sac` | Atendimento |
| `scrap` | Web scraping |

**Financeiro:**

| Sigla | Categoria |
|-------|-----------|
| `analise` | Analise de dados |
| `contas` | Contas a pagar/receber |
| `fiscal` | Fiscal e tributario |
| `orcamento` | Orcamento e planejamento |
| `conciliacao` | Conciliacao bancaria |
| `pmo` | Gestao e relatorios gerenciais |

**Logistica:**

| Sigla | Categoria |
|-------|-----------|
| `analise` | Analise de dados |
| `frete` | Frete e transportadoras |
| `estoque` | Gestao de estoque |
| `separacao` | Separacao de pedidos |
| `rota` | Roteirizacao |
| `pmo` | Gestao e relatorios gerenciais |

**RH:**

| Sigla | Categoria |
|-------|-----------|
| `analise` | Analise de dados |
| `recrutamento` | Recrutamento e selecao |
| `treinamento` | Treinamento e desenvolvimento |
| `folha` | Folha de pagamento |
| `pmo` | Gestao e relatorios gerenciais |

Defina suas categorias no CLAUDE.md raiz do workspace.

---

## Arquivos obrigatorios

Todo projeto deve conter no minimo estes 3 arquivos:

### CLAUDE.md — briefing do projeto

O que e: manual que o Claude Code le ao entrar na pasta. Contem contexto, regras, arquivos importantes e comandos especificos do projeto.

Formato:

```markdown
# Nome do Projeto

## Contexto
[O que esse projeto faz e por que existe]

## Arquivos importantes
- dados_vendas.xlsx: exportacao do ERP com vendas dos ultimos 6 meses
- script_processar.py: pipeline de limpeza e agregacao

## Registro de progresso no banco PMO (automatico)

Para registrar atividades deste projeto:

import sys; sys.path.insert(0, r'C:\Users\USUARIO\Desktop\WORKSPACE')
from pmo_db import log_activity
log_activity('2026-04-07', 'nome-projeto', 'feature', 'Descricao do que foi feito')

## Comandos

### /fechar-projeto
Atualiza o CLAUDE.md e historico.md desta pasta com o estado atual do trabalho.
```

### historico.md — registro cronologico

O que e: diario do projeto. Cada entrada tem data, tipo e descricao. O Claude Code adiciona entradas conforme trabalha.

Formato:

```markdown
# Historico - Nome do Projeto

## 2026-04-07
- [feature] Projeto criado com estrutura padrao
- [config] Configurado pipeline de dados com pandas

## 2026-04-08
- [analysis] Analise exploratoria dos dados de vendas
- [discovery] Encontrado gap de 15% nos registros de marco
- [decision] Definido usar media movel de 3 meses para preencher gaps
```

Tipos validos para os colchetes:

| Tipo | Quando usar |
|------|-------------|
| `decision` | Escolha que afeta o rumo do projeto |
| `bugfix` | Correcao de erro |
| `feature` | Funcionalidade nova |
| `discovery` | Achado relevante nos dados |
| `refactor` | Reorganizacao de codigo sem mudar funcionalidade |
| `config` | Configuracao de ambiente ou ferramenta |
| `analysis` | Resultado de analise |
| `change` | Alteracao generica |

### proximos-passos.md — lista de retomada

O que e: o arquivo que o Claude Code le ANTES de comecar qualquer trabalho no projeto. Contem o estado atual, acoes pendentes, dependencias e bugs conhecidos. Sem este arquivo, o Claude precisa reler todo o historico para entender onde parou.

Formato:

```markdown
# Proximos Passos

## Situacao atual
Pipeline de dados funcionando. Analise exploratoria completa. Falta gerar
o dashboard final e enviar por email.

## Acoes pendentes
1. [PRIORIDADE] Gerar dashboard HTML com grafico de vendas por mes
2. [PRIORIDADE] Enviar dashboard por email para diretoria
3. [NORMAL] Adicionar filtro por categoria de produto
4. [FUTURO] Automatizar execucao semanal via cron

## Dependencias
- Aguardando lista de emails da diretoria (pedir para o gestor)
- Dados de abril so disponiveis apos dia 5

## Bugs conhecidos
- Coluna "preco" vem com virgula no CSV, precisa converter para float (workaround: .str.replace(',','.').astype(float))
```

CRITICO: Este arquivo e o que permite retomada de trabalho entre sessoes. Atualize-o ao final de cada sessao de trabalho.

---

## Subpastas do projeto

Estrutura recomendada de subpastas dentro de cada projeto:

```
YYYYMM_categoria_nome-projeto/
  CLAUDE.md              — briefing do projeto
  historico.md           — registro cronologico
  proximos-passos.md     — retomada entre sessoes
  01_input/              — dados de entrada brutos, instrucoes de fonte
  02_processar/          — regras de transformacao, mapeamentos
  03_analisar/           — subtarefas de analise
  04_output/             — template de entrega
  dados/                 — arquivos intermediarios gerados pelo processamento
  scripts/               — scripts Python do projeto
  saidas/                — entregas finais (HTML, XLSX, CSV)
```

### Subtarefas em 03_analisar/

Para analises complexas com multiplas etapas, crie subpastas numeradas:

```
03_analisar/
  tarefa_01_limpeza/
    execute.md           — instrucoes para executar a tarefa
    resultado.md         — resultado da execucao
  tarefa_02_agregacao/
    execute.md
    resultado.md
```

Cada `execute.md` deve ser autossuficiente: o Claude Code le e executa sem contexto adicional.

---

## Pasta PMO (000000)

A pasta com prefixo `000000` e especial:

- Fica sempre no topo da listagem alfabetica de pastas
- Usada para consolidacao: relatorios mensais, analytics, dashboards gerenciais
- Contem templates reutilizaveis e scripts de gestao

Exemplo: `000000_pmo_analytics-gestor/`

Conteudo tipico:
- Relatorios mensais (RELATORIO_ABR2026.html)
- Scripts de consolidacao
- Templates de email
- Configuracoes de integracao (proxy MCP, etc.)

---

## Sistema PMO (banco SQLite)

O framework usa SQLite como fonte primaria de dados de gestao. Nunca dependa apenas de arquivos .md para consultas — o banco e mais rapido e confiavel.

### Componentes

| Arquivo | Funcao |
|---------|--------|
| `pmo.db` | Banco SQLite com tabelas: sessions, activities, pending, projects, objectives |
| `pmo_db.py` | Modulo Python com funcoes de acesso ao banco |
| `pmo_setup.py` | Script que cria pasta de projeto completa com 1 comando |
| `GLOSSARIO.md` | Indice legivel de todos os projetos com status |
| `DIARIO.md` | Registro consolidado das atividades de cada dia |

### Funcoes principais de pmo_db.py

```python
# Iniciar banco (so precisa rodar 1 vez)
from pmo_db import init_db
init_db()

# Iniciar sessao de trabalho — retorna session_id
from pmo_db import session_start
sid = session_start('Trabalhando em analise de vendas')

# Registrar atividade
from pmo_db import log_activity
log_activity('2026-04-07', 'vendas-regiao', 'analysis', 'Analise exploratoria completa', session_id=sid)

# Encerrar sessao
from pmo_db import session_end
session_end(sid, 'Dashboard gerado e enviado')

# Consultas
from pmo_db import list_pending, project_stats, search_activities, session_context, inactive_projects
list_pending()              # pendencias abertas
project_stats()             # estatisticas gerais
search_activities('vendas') # busca por texto
session_context(3)          # ultimas 3 sessoes
inactive_projects(30)       # projetos sem atividade ha 30 dias
```

---

## Protocolo de sessao

Toda sessao de trabalho segue este protocolo:

### 1. Inicio

```python
python -c "from pmo_db import session_start; print(session_start('Resumo do que sera feito'))"
```

Guardar o session_id retornado.

### 2. Orientacao

- Ler `proximos-passos.md` do projeto que sera trabalhado
- Se nao existir, ler `historico.md` para entender o contexto
- Se o projeto nao tiver CLAUDE.md, criar antes de comecar

### 3. Trabalho

- Executar as tarefas
- A cada marco significativo, registrar:

```python
python -c "from pmo_db import log_activity; log_activity('2026-04-07', 'nome-projeto', 'feature', 'Descricao do marco', session_id=ID)"
```

### 4. Atualizacao

- Adicionar entradas no `historico.md` do projeto
- Atualizar `proximos-passos.md` com novo estado

### 5. Encerramento

```python
python -c "from pmo_db import session_end; session_end(ID, 'Resumo do que foi feito na sessao')"
```

---

## Comandos

### /nova-pasta

Cria novo projeto padronizado.

1. Pergunte ao usuario: nome, categoria e descricao
2. Execute:

```python
python -c "from pmo_setup import nova_pasta; nova_pasta('nome-projeto', 'categoria', 'Descricao do projeto')"
```

Isso cria automaticamente: pasta com nome padronizado, CLAUDE.md, historico.md, subpastas, registro no pmo.db, entrada no GLOSSARIO.md.

### /fechar-dia

Consolida atividades do dia.

1. Consulte atividades do dia no banco:
```python
python -c "from pmo_db import query_activities; import json; print(json.dumps(query_activities('date = ?', ('2026-04-07',), 100), indent=2, ensure_ascii=False))"
```
2. Encerre a sessao ativa: `session_end(session_id, 'resumo')`
3. Atualize status no `GLOSSARIO.md`
4. Adicione entrada no `DIARIO.md`
5. Atualize `historico.md` de cada projeto trabalhado

Formato da entrada no DIARIO.md:

```markdown
## 2026-04-07

### Projetos trabalhados
- `202604_analise_vendas-regiao`: Analise exploratoria e dashboard

### O que foi feito
- [analysis] Analise exploratoria dos dados de vendas por regiao
- [feature] Dashboard HTML gerado com graficos interativos

### Pendencias
- Enviar dashboard por email apos validacao

---
```

### /status

Consulta rapida de estado via SQLite:

```python
python -c "from pmo_db import session_last; print(session_last())"
python -c "from pmo_db import query_activities; print(query_activities(limit=10))"
python -c "from pmo_db import list_pending; print(list_pending())"
python -c "from pmo_db import inactive_projects; print(inactive_projects(30))"
python -c "from pmo_db import project_stats; print(project_stats())"
```

### /fechar-projeto

Finaliza documentacao de um projeto:

1. Atualize `CLAUDE.md` com estado final
2. Adicione entrada final no `historico.md`
3. Remova ou arquive `proximos-passos.md`
4. Atualize status no `GLOSSARIO.md` para "Concluido"

---

## 10 boas praticas

1. **Sempre atualize historico.md ao concluir trabalho.** E o registro permanente do projeto. Se nao esta no historico, nao aconteceu.

2. **Use proximos-passos.md para retomada entre sessoes.** Sem ele, o Claude precisa reler tudo. Com ele, retoma em segundos.

3. **Registre decisoes (tipo decision).** Decisoes sao o contexto mais valioso para o futuro. "Por que fizemos X em vez de Y" evita retrabalho.

4. **Nao deixe projetos sem CLAUDE.md.** Uma pasta sem CLAUDE.md e invisivel para o framework. O Claude nao sabe o que fazer com ela.

5. **Nomes de pasta sempre minusculos com hifens.** `vendas-por-regiao`, nunca `Vendas_Por_Regiao` ou `vendasPorRegiao`.

6. **Dados intermediarios em dados/, nunca na raiz do projeto.** A raiz deve ter apenas os 3 arquivos obrigatorios e as subpastas padrao.

7. **Entregas finais em saidas/ com data no nome.** Exemplo: `saidas/dashboard_vendas_20260407.html`. Permite rastrear versoes.

8. **Console Windows: nunca emojis em print().** Use marcadores ASCII: `[OK]`, `[ERRO]`, `[INFO]`, `[AVISO]`. Emojis causam UnicodeEncodeError no cp1252.

9. **CSV de saida: encoding='utf-8-sig' para Excel BR.** O BOM (Byte Order Mark) faz o Excel abrir o arquivo com acentos corretos.

10. **Um projeto = um escopo.** Se o escopo muda significativamente, crie nova pasta. Projetos guarda-chuva viram confusos rapidamente.
