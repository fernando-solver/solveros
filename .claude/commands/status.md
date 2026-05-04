---
description: Consulta rapida do estado do workspace
---

Execute o comando `/status` conforme a secao "## /status" do CLAUDE.md na raiz.

Execute via Bash os seguintes comandos e apresente um resumo consolidado:

```bash
python -c "from pmo_db import session_last, query_activities, list_pending, inactive_projects, project_stats, list_objectives; import json; print(json.dumps({'ultima_sessao': session_last(), 'atividades_recentes': query_activities(limit=10), 'pendencias': list_pending(), 'projetos_inativos': inactive_projects(30), 'objetivos_ativos': list_objectives(), 'stats_projetos': project_stats()[:10]}, indent=2, ensure_ascii=False, default=str))"
```

Apresente ao usuario em bullets curtos:

- **Ultima sessao:** data + resumo (se encerrada) ou "em andamento"
- **Atividades recentes:** 10 ultimas
- **Pendencias abertas:** count + top 3
- **Projetos inativos (30d+):** count + lista
- **Objetivos ativos:** count + titulos
- **Top 3 projetos por volume:** lista

Nao despeje o JSON bruto — resuma em linguagem humana.
