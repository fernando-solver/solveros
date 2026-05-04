# Skills

## O que sao

Skills sao a **terceira camada de memoria** do Solver Filesystem. Alem do contexto declarativo (`.md` dos projetos) e do log de eventos (`pmo.db`), as skills armazenam **memoria procedural auto-melhoravel** — procedimentos que o agente consolidou ao resolver problemas complexos, reutilizaveis entre projetos, com historico de melhoria versionado.

## Descoberta automatica (novidade v0.2)

Em vez de o usuario precisar lembrar que skills existem, o PMO descobre sozinho via `find_skill_local()`. Ranking combina:

- Relevancia de texto (FTS5 BM25) — match em `name + description + trigger`
- Historico de uso (`uses_count` com peso logaritmico)
- Recencia (bonus se usada nos ultimos 30 dias)

Veja `skill_find-skill-local.md` para o procedimento completo.

## Regra pratica

- Resolveu algo complexo que provavelmente sera util de novo? → **consolide como skill**
- Usou uma skill existente e viu oportunidade de melhoria? → **registre `improvement_noted` no `log_skill_use`**; o PMO revisa periodicamente
- Ja tem 5+ skills e o catalogo esta dificil de navegar? → **adicione tags na frontmatter** (YAGNI ate la)

## Estrutura de uma skill

Cada skill e um arquivo `.md` nesta pasta com frontmatter minimo:

```markdown
---
name: skill_NN_nome-curto
description: O que faz em 1 frase
trigger: Quando usar (texto livre)
version: 1
last_updated: YYYY-MM-DD
uses_count: 0
---

## Procedimento
[passos executaveis]

## Historico de melhoria
- v1 (YYYY-MM-DD): versao inicial
```

## Como o agente usa

### Descobrir skill para uma tarefa

```python
python -c "
from pmo_db import find_skill_local
import json
print(json.dumps(find_skill_local('preciso analisar um xlsx', limit=5), indent=2, ensure_ascii=False))
"
```

### Ao resolver problema complexo, consolidar

```python
python -c "
from pmo_db import register_skill
register_skill(
    name='skill_NN_nome-curto',
    description='O que faz',
    trigger='Quando usar',
    file_path='skills/skill_NN_nome-curto.md'
)
"
```

E cria o arquivo `.md` seguindo o template acima.

### Ao usar skill existente

```python
python -c "
from pmo_db import skill_by_name, log_skill_use
s = skill_by_name('skill_NN_nome')
# ...executa o procedimento da skill...
log_skill_use(s['id'], 'nome-projeto', outcome='sucesso', session_id=SID)
"
```

Se voce ve oportunidade de melhoria durante o uso, passe `improvement_noted='descricao'`.

Revisao periodica de melhorias pendentes:

```python
python -c "from pmo_db import skill_improvements_pending; print(skill_improvements_pending())"
```

### Rebuild do indice FTS (raro)

Se suspeitar que a busca ficou dessincronizada (ex: edicoes SQL manuais):

```python
python -c "from pmo_db import fts_rebuild_skills; fts_rebuild_skills()"
```

## Regra de auto-aplicacao de melhorias

- **Mudanca pequena** (corrigir bug evidente, ajustar regex, adicionar caso edge comprovado) → agente aplica direto na skill canonica, bumpa `version`, atualiza `last_updated`.
- **Mudanca grande** (reescrever procedimento, mudar schema, deprecar) → agente **nao aplica**, apenas registra `improvement_noted`. PMO revisa periodicamente e decide.

## Catalogo inicial (kit v0.3)

Cinco skills ja vem instaladas. Delete ou adapte conforme precisar:

| Skill | Categoria | Quando usar |
|---|---|---|
| `skill_find-skill-local` | Sistema | PMO descobre skills relevantes para uma tarefa |
| `skill_compartilhar-projeto` | **Sistema (v0.3)** | Empacotar projeto em ZIP curado para handoff a colaborador |
| `skill_ver-dashboard` | **Sistema (v0.3)** | Gerar dashboard HTML de retrato do trabalho |
| `skill_exemplo_01_analisar-planilha-excel` | Exemplo | Analise exploratoria de planilha Excel |
| `skill_exemplo_02_resumo-executivo` | Exemplo | Resumo executivo em 3 camadas de texto longo |

As tres skills de Sistema sao usadas pelo PMO para auto-roteamento (`find-skill-local`), exportacao curada de projeto (`compartilhar-projeto`) e visualizacao (`ver-dashboard`). As outras sao exemplos didaticos que voce pode usar, adaptar ou remover.
