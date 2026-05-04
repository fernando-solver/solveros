# PMO Consolidacao

## Contexto

Pasta especial (prefixo `000000`) que fica sempre no topo da listagem alfabetica. E a "sala da diretoria" do workspace — contem relatorios gerenciais, consolidacoes, templates reutilizaveis e scripts de gestao que atravessam projetos.

## Responsavel

[PREENCHER - responsavel]

## O que vive aqui

Exemplos do que e apropriado criar nesta pasta conforme o workspace evolui:

- `relatorios/` — relatorios mensais do estado do workspace (gerados via consultas ao `pmo.db`)
- `templates/` — modelos reutilizaveis de email, dashboard HTML, briefings padrao
- `scripts/` — scripts de consolidacao e gestao que nao pertencem a nenhum projeto especifico
- `playbooks/` — procedimentos operacionais consolidados (ex: "como fazer fechamento mensal")

## O que NAO vive aqui

- Projetos operacionais especificos — esses vao em suas proprias pastas `YYYYMM_categoria_nome/`
- Dados brutos — esses ficam nas pastas dos projetos que os usam

## Comandos relevantes

### Relatorio mensal do workspace

Gerado tipicamente no primeiro dia do mes, consolidando o anterior:

```python
python -c "
from pmo_db import query_activities, project_stats, objective_dashboard
import json
# exemplo: todas atividades do mes passado
print(json.dumps(query_activities('date >= ? AND date <= ?', ('YYYY-MM-01', 'YYYY-MM-31'), 500), indent=2))
"
```

### Auditoria de saude do workspace

```python
python -c "
from pmo_db import inactive_projects, orphan_projects
print('Projetos inativos:', inactive_projects(30))
print('Projetos sem objetivo:', orphan_projects())
"
```

## Registro de progresso

Atividades criadas aqui sao registradas no banco com project='000000_pmo_consolidacao':

```python
python -c "
from pmo_db import log_activity
log_activity('YYYY-MM-DD', '000000_pmo_consolidacao', 'tipo', 'Descricao do que foi feito')
"
```
