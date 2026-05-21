---
name: skill_pessoal_04_arquivar-pasta
description: Move pasta inativa pra _archive/<ano>Q<n>/ seguindo o padrao SolverOS, sem perder historico
trigger: O usuario pede "arquiva essa pasta", "tira essa daqui" ou voce identifica pasta sem mudancas ha 90+ dias
version: 1
last_updated: 2026-05-03
uses_count: 0
---

# Arquivar pasta inativa

## Quando usar

- Pasta de projeto sem modificacao ha 90+ dias
- Projeto entregue/finalizado que ja nao precisa estar visivel
- Limpeza de fim de trimestre
- Usuario pede explicitamente "tira essa pasta da minha frente"

## Quando NAO usar

- Pasta com atividade nos ultimos 30 dias — pergunte antes
- Pasta sem `historico.md` — pode ser arquivo isolado, nao projeto
- Usuario nao confirmou explicitamente — confirme antes de mover

## Procedimento

### 1. Confirma idade da pasta

```python
from pathlib import Path
import time
from datetime import datetime, timedelta

pasta = Path('caminho/da/pasta')

# Encontra arquivo modificado mais recentemente
ultima_mod = max(
    (f.stat().st_mtime for f in pasta.rglob('*') if f.is_file()),
    default=0
)

dias_inativa = (time.time() - ultima_mod) / 86400
print(f'Ultima modificacao: {dias_inativa:.0f} dias atras')

if dias_inativa < 30:
    print('[AVISO] Pasta tem atividade recente — confirma antes de arquivar?')
```

### 2. Confirma com o usuario

```
A pasta '<nome>' tem ultima atividade ha <N> dias.
Vou mover pra `_archive/<ano>Q<n>/<nome>/`.

Confirma? (sim / nao)
```

So prossegue se for explicitamente "sim".

### 3. Calcula destino

```python
hoje = datetime.now()
ano = hoje.year
trimestre = (hoje.month - 1) // 3 + 1
destino_base = Path(f'_archive/{ano}Q{trimestre}')
destino_base.mkdir(parents=True, exist_ok=True)
destino = destino_base / pasta.name
```

### 4. Move + registra

```python
import shutil
from pmo_db import log_activity

shutil.move(str(pasta), str(destino))

log_activity(
    date=hoje.strftime('%Y-%m-%d'),
    project=pasta.name,
    tipo='change',
    description=f'Arquivada em {destino} (inativa ha {dias_inativa:.0f} dias)'
)
```

### 5. Atualiza GLOSSARIO.md

Marca o projeto como "Arquivado" no glossario, com link pra nova
localizacao:

```python
glossario = Path('GLOSSARIO.md')
texto = glossario.read_text(encoding='utf-8')
nova_linha = f'| `{pasta.name}` | <descricao mantida> | Arquivado em {destino} |'
# Substitui a linha antiga ou adiciona se nao existe
```

### 6. Devolve ao usuario

```
[OK] Arquivada.

Pasta: <nome>
Movida pra: _archive/<ano>Q<n>/<nome>/
Registrado no pmo.db e GLOSSARIO.md atualizado.

Pra recuperar: shutil.move(_archive/.../<nome>, raiz)
```

## Output esperado

Pasta movida + log no SQLite + atualizacao no `GLOSSARIO.md`.

## Erros comuns

- **Permissao negada** → arquivo aberto em outro programa, peca pra
  fechar e tentar de novo
- **Pasta vazia** → ainda assim mova, registre como "esqueleto vazio
  arquivado"
- **`_archive/` ja tem pasta com mesmo nome** → adiciona sufixo
  `_<YYYYMMDD>` ao nome no destino
- **`pmo.db` ou `GLOSSARIO.md` nao existem** → arquiva mesmo assim,
  sinaliza no terminal
