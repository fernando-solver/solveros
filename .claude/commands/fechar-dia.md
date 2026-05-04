---
description: Consolidar atividades do dia no DIARIO.md
---

Execute o comando `/fechar-dia` conforme a secao "## /fechar-dia" do CLAUDE.md na raiz.

Fluxo:

1. Descubra a data de hoje (YYYY-MM-DD).

2. Consulte atividades do dia:

```bash
python -c "
from pmo_db import query_activities
import json
print(json.dumps(query_activities('date = ?', ('YYYY-MM-DD',), 200), indent=2, ensure_ascii=False))
"
```

3. Encerre a sessao ativa (se houver session_id em memoria):

```bash
python -c "from pmo_db import session_end; session_end(SID, 'Resumo do dia')"
```

4. Atualize `DIARIO.md` com entrada consolidada do dia:
   - Projetos trabalhados (lista)
   - O que foi feito (resumo por tipo)
   - Pendencias novas que apareceram

5. Atualize `historico.md` de cada projeto trabalhado com entrada do dia.

6. Atualize coluna "Status" no `GLOSSARIO.md` se algum projeto mudou de estado.

7. Confirme ao usuario: sessao encerrada, DIARIO.md atualizado, historicos dos projetos consolidados.
