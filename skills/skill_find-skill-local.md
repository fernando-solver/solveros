---
name: skill_find-skill-local
description: Descobre skills locais relevantes para uma tarefa antes de spawn de subagente
trigger: PMO vai spawnar subagente; usuario pergunta "tem skill pra X?"; precisa descobrir capacidades disponiveis no workspace
version: 1
last_updated: 2026-04-22
uses_count: 0
---

# Descoberta de skills locais

## Quando usar

- Antes de spawnar subagente — PMO descobre automaticamente qual skill recomendar no prompt inicial
- Quando o usuario pergunta "tem skill pra X?" ou "como eu faco Y?"
- Em `/status` — listar top skills do workspace ordenadas por uso
- Auditoria periodica — skills sem uso em 30+ dias podem estar obsoletas

## Quando NAO usar

- Se voce ja sabe exatamente qual skill usar (passe direto para o spawn)
- Se a tarefa e totalmente nova e nao ha chance de haver skill pronta (criar nova)

## Procedimento

### 1. Capture uma descricao curta da tarefa

Uma frase em linguagem natural, tipo "preciso analisar esse xlsx de vendas" ou "quero um resumo dessa transcricao de reuniao".

### 2. Consulte o catalogo local

```python
python -c "
from pmo_db import find_skill_local
import json
print(json.dumps(find_skill_local('preciso analisar esse xlsx de vendas', limit=5), indent=2, ensure_ascii=False))
"
```

O ranking interno combina:
- **Relevancia** — match FTS5 BM25 em `name + description + trigger` (peso 2.0)
- **Historico de uso** — `uses_count` com peso logaritmico (peso 0.5)
- **Recencia** — bonus 0.3 se a skill foi usada nos ultimos 30 dias

### 3. Interprete o resultado

**Caso A — resultado forte (top score destacado):** recomende a top 1 ao usuario ou injete no prompt do subagente.

**Caso B — resultados fracos (todos com score baixo e similar):** provavelmente nenhuma skill existente resolve bem. Opcoes:
- Criar skill nova para esta tarefa (se e algo que vai repetir)
- Buscar no ecossistema publico: `npx skills find "<query>"` (ferramenta do Vercel Labs em https://skills.sh/)

**Caso C — resultado vazio:** nenhuma skill cadastrada combina. Siga caminhos de Caso B.

### 4. Integracao com spawn de subagente

Ao spawnar subagente para executar uma tarefa, o PMO inclui no prompt inicial:

> "Skills recomendadas para esta tarefa: [skill_01_extrair-palestra]. Leia o arquivo skills/skill_01_extrair-palestra.md antes de executar."

Isso economiza contexto — o subagente le a skill especifica ao inves de escanear toda a pasta `skills/`.

### 5. Registro de uso

Depois de executar com uma skill, registre para alimentar o ranking futuro:

```python
python -c "
from pmo_db import skill_by_name, log_skill_use
s = skill_by_name('skill_01_extrair-palestra')
log_skill_use(s['id'], 'nome-projeto', outcome='sucesso', session_id=ID)
"
```

Se identificou oportunidade de melhoria, passe tambem `improvement_noted='...'`.

## Exemplo real de saida

Query: `"preciso analisar um xlsx"`

```json
[
  {
    "id": 1,
    "name": "skill_exemplo_01_analisar-planilha-excel",
    "description": "Analise exploratoria de planilha Excel desconhecida",
    "trigger": "Usuario pede para entender xlsx",
    "uses_count": 3,
    "version": 1,
    "fts_score": 4.2,
    "recent_uses": 2
  }
]
```

Score alto, skill clara, usada recentemente. PMO recomenda sem hesitar.

## Sinais de melhoria

- **Top result tem score baixo consistentemente:** o catalogo esta pobre para este dominio — criar skill nova.
- **Skill errada aparece alta:** trigger esta mal escrito — reescrever o campo `trigger` da skill certa para capturar a intencao.
- **Queries em ingles nao retornam skills em pt-br:** se o workspace e multilingue, adicionar traducao no campo `description`.
- **FTS dessincronizado:** rodar `python -c "from pmo_db import fts_rebuild_skills; fts_rebuild_skills()"`.

## Historico de melhoria

- v1 (2026-04-22): versao inicial — ranking BM25 + uses_count (log) + recencia.
