---
name: skill_pessoal_02_revisar-semana
description: Le o historico das ultimas 7 sessoes e gera relatorio do que evoluiu, travou ou merece atencao
trigger: O usuario pede uma "revisao da semana", "como foi minha semana" ou "o que andei fazendo"
version: 1
last_updated: 2026-05-03
uses_count: 0
---

# Revisão semanal

## Quando usar

- Final de sexta-feira ou começo de segunda
- Usuario sente que "trabalhou muito mas não sabe no que"
- Antes de uma reuniao 1:1 ou planejamento da próxima semana
- Quando o objetivo principal está há vários dias sem ser tocado

## Quando NAO usar

- Workspace recém-criado (< 5 sessões registradas) — não tem dado
  suficiente
- Pedido genérico de "como vai" sem contexto temporal

## Procedimento

### 1. Pega atividades dos últimos 7 dias

```python
from pmo_db import query_activities, objetivo_list, session_last
from collections import Counter

atividades = query_activities("date >= date('now', '-7 days')", (), 200)
print(f'{len(atividades)} atividades nos ultimos 7 dias')

# Distribui por projeto
por_projeto = Counter(a['project'] for a in atividades)
# Distribui por tipo
por_tipo = Counter(a['tipo'] for a in atividades)
```

### 2. Identifica padrões

- **Projeto que mais avancou** = mais atividades de tipo `feature` ou
  `discovery`
- **Projeto que travou** = atividades só de tipo `bugfix` ou `decision`
  sem `feature` subsequente
- **Projeto abandonado** = projetos ativos no `pmo.db` sem atividade na
  semana

```python
features_por_projeto = Counter(
    a['project'] for a in atividades if a['tipo'] == 'feature'
)
bugfixes_por_projeto = Counter(
    a['project'] for a in atividades if a['tipo'] == 'bugfix'
)
```

### 3. Cruza com objetivos

```python
objetivos = objetivo_list()
principal = next((o for o in objetivos if o['tipo'] == 'meta_30_dias'), None)

if principal:
    # tocou no objetivo principal essa semana?
    atividades_obj = [a for a in atividades
                      if principal['descricao'].lower() in a['description'].lower()]
    print(f'{len(atividades_obj)} atividades tocaram no objetivo principal')
```

### 4. Gera relatorio em saidas/revisao_<YYYYMMDD>.md

```markdown
# Revisão semanal — semana de <DD-DD/MM>

## TL;DR
<frase de 1 linha que resume a semana>

## Números
- Total de atividades: <N>
- Sessões de trabalho: <M>
- Projetos tocados: <X>
- Atividades alinhadas com objetivo principal: <Y> de <N>

## Destaques
- ✅ **Avançou:** <projeto> — <que tipo de avanco>
- ⚠️ **Travou:** <projeto> — <sintoma observado>
- 💤 **Sem mexer:** <projeto> (X dias sem atividade)

## Objetivo principal
<descrição do objetivo>
Status: <X% das atividades foram alinhadas / abandonado há N dias / em ritmo>

## Sugestão pra próxima semana
<1 ação concreta — não 5>
```

### 5. Devolve ao usuario

Mande TL;DR + 1 sugestão direto no terminal:

```
[OK] Revisão da semana gerada.

TL;DR: <frase>

Sugestão: <1 ação>

Relatório completo: saidas/revisao_<data>.md
```

## Output esperado

Arquivo markdown em `saidas/` + resumo de 3 linhas no terminal.

## Erros comuns

- **`pmo.db` vazio** → diz "registre algumas atividades primeiro com
  `log_activity()` ou rode trabalho real essa semana"
- **Sem objetivo principal cadastrado** → pula seção "Objetivo
  principal" e sugere `/setup-pessoal` pra cadastrar
