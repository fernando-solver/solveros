---
name: skill_pessoal_01_organizar-leitura
description: Organiza pasta de PDFs/artigos por tema e marca os 3 mais relevantes pra ler primeiro
trigger: O usuario tem uma pasta com PDFs, artigos ou e-books bagunçados e pede pra "organizar", "indexar" ou "saber por onde comecar"
version: 1
last_updated: 2026-05-03
uses_count: 0
---

# Organizar pasta de leitura

## Quando usar

- Pasta com 5+ PDFs/artigos sem ordem clara
- Usuario diz "tenho um monte de coisa pra ler e nao sei por onde começar"
- Backlog de leitura acumulada que virou paralisia

## Quando NAO usar

- Menos de 5 arquivos — só abra e olhe
- PDFs ja organizados em subpastas — só falta sumarizar, use `skill_pessoal_03_resumo-projeto`
- Artigos curtos (< 5 paginas) — leia direto

## Procedimento

### 1. Mapeia a pasta

```python
from pathlib import Path
import PyPDF2  # pip install PyPDF2

pasta = Path('caminho/da/pasta')
pdfs = list(pasta.glob('*.pdf'))
print(f'Encontrados {len(pdfs)} PDFs')

for p in pdfs:
    try:
        with open(p, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_paginas = len(reader.pages)
            primeira_pag = reader.pages[0].extract_text()[:500]
            print(f'\n--- {p.name} ({num_paginas}p) ---')
            print(primeira_pag)
    except Exception as e:
        print(f'[ERRO] {p.name}: {e}')
```

### 2. Agrupa por tema

Lendo o título + primeiros parágrafos de cada PDF, agrupe em 3-5 temas
inferidos. Use vocabulário do próprio usuário se houver `objetivos.md`
ou `CLAUDE.md` na pasta — sinaliza interesse atual.

### 3. Pontua relevância (1 a 5)

Critérios:
- **+2** se o tema bate com objetivo ativo do usuário (ler `objetivos.md`)
- **+1** se foi adicionado nos últimos 30 dias (data de modificação)
- **+1** se < 30 páginas (quick win pra desbloquear leitura)
- **-1** se > 200 páginas e tema secundário (vai roubar muito tempo)

### 4. Gera INDICE.md na pasta

```markdown
# Índice de leitura — gerado em 2026-05-03

## TOP 3 — comece por aqui
1. **<titulo>** (<paginas>p, <tema>) — <razao em 1 linha>
2. **<titulo>** (<paginas>p, <tema>) — <razao em 1 linha>
3. **<titulo>** (<paginas>p, <tema>) — <razao em 1 linha>

## Por tema

### <Tema 1>
- <titulo> (<paginas>p)
- <titulo> (<paginas>p)

### <Tema 2>
- ...

## Backlog (deixe pra depois)
- <titulo>
- <titulo>
```

### 5. Devolve ao usuario

```
[OK] Indexei <N> PDFs em <M> temas.

Top 3 pra começar:
  1. <titulo> — <razao>
  2. <titulo> — <razao>
  3. <titulo> — <razao>

Indice completo: <pasta>/INDICE.md
```

## Output esperado

Arquivo `INDICE.md` na raiz da pasta + lista TOP 3 no terminal.
Usuario sabe o que ler primeiro em < 30 segundos depois de abrir o
INDICE.

## Erros comuns

- **PDF protegido por senha** → pula, registra em `INDICE.md` na seção
  "Falhei em ler"
- **PDF escaneado sem OCR** → primeira_pag vai ser vazio; classifica
  como "Não consegui ler conteúdo" e sugere OCR manual
