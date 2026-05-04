---
description: Empacotar projeto em ZIP curado para handoff a colaborador
argument-hint: [nome-projeto] [destinatario]
---

Execute o comando `/compartilhar` conforme a secao "## /compartilhar <projeto> [destinatario]" do CLAUDE.md na raiz.

Fluxo:

1. Confirme com o usuario qual projeto compartilhar e quem e o destinatario (opcional).

2. Execute via Bash:

```bash
python -c "
from pmo_share import share_project
import json
r = share_project('<PROJETO>', destinatario='<NOME>')
print(json.dumps(r, indent=2, ensure_ascii=False))
"
```

3. Interprete o retorno:
   - Se `cred_warnings` nao-vazio: **avise o usuario** para revisar os arquivos listados antes de enviar
   - Mostre o caminho do ZIP (`zip_path`), tamanho (`size_bytes`) e contagem (`files_count`)

4. Sugira como enviar o ZIP (email, Drive, Dropbox) e a instrucao para o destinatario:
   "Extraia o ZIP, abra Claude Code na pasta e diga 'assumir projeto compartilhado'."

Detalhes completos em `skills/skill_compartilhar-projeto.md`.

Argumentos recebidos: $ARGUMENTS
