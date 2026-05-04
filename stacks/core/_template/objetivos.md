# Objetivos deste projeto

Os objetivos abaixo sao sincronizados com o `pmo.db`. Edite preferencialmente
via `objetivo_add` / `objetivo_update` pra manter a fonte unica.

## Como ler

| Tipo (exemplo) | O que mede |
|---|---|
| `meta_30_dias` | KPI livre que voce define pros proximos 30 dias |
| `entregas_mes` | numero de entregas concluidas por mes |
| `horas_foco_dia` | horas de trabalho profundo por dia |
| `progresso_aprendizado` | avanco em curso, livro ou skill nova |
| `<livre>` | qualquer KPI relevante pra voce |

## Visualizar atuais

```python
from pmo_db import objetivo_list
for o in objetivo_list():
    print(o)
```

## Adicionar objetivo

```python
from pmo_db import objetivo_add
objetivo_add(
    tipo='meta_30_dias',
    descricao='Terminar o primeiro rascunho do livro',
    alvo=1,
    unidade='rascunho',
    prazo='2026-05-31'
)
```
