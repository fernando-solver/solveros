---
name: skill_compartilhar-projeto
description: Empacota projeto em ZIP curado para handoff a colaborador, com scrub de credenciais e paths
trigger: Usuario pede compartilhar projeto; encerramento com entrega a cliente; passar trabalho para outro membro do time
version: 1
last_updated: 2026-04-23
uses_count: 0
---

# Compartilhar projeto (handoff curado)

## Quando usar

- Usuario pede: "compartilha esse projeto com Pedro", "manda pro cliente", "preciso passar pra outra pessoa"
- Fim de consultoria / handoff entre membros do time
- Documentar estado do projeto em snapshot (mesmo sem compartilhar)

## Quando NAO usar

- Se a pasta tem muitos arquivos binarios pesados (videos, imagens raw) — avaliar manualmente antes
- Se ha dados sensiveis em formatos nao-texto (PDFs, imagens com OCR) — share nao consegue escanear esses formatos; alertar usuario

## Procedimento

### 1. Colete informacoes

- Nome exato da pasta de projeto (ex: `202604_analise_vendas-regiao`)
- Destinatario (opcional, vira metadado no pmo.db): nome, email, papel

### 2. Execute

```python
python -c "
from pmo_share import share_project
import json
r = share_project(
    project_folder='202604_analise_vendas-regiao',
    destinatario='pedro@empresa.com',
    notes='Handoff para Pedro dar continuidade apos viagem'
)
print(json.dumps(r, indent=2, ensure_ascii=False))
"
```

### 3. Leia o resultado

O dict retornado tem:
- `zip_path` — caminho absoluto do ZIP gerado (em `<projeto>/shared/<projeto>_handoff_YYYYMMDD.zip`)
- `size_bytes` — tamanho do ZIP
- `files_count` — arquivos dentro
- `excluded_count` — arquivos que ficaram de fora (local.md, sensitive, intermediarios grandes)
- `cred_warnings` — lista de `[(arquivo, tipo)]` onde foi detectada possivel credencial
- `integrity_ok` — True se ZIP passa no `testzip()`

### 4. Se cred_warnings nao-vazio, AVISE o usuario ANTES de entregar

Exemplo de fala:

> "Gerei o ZIP, mas detectei possiveis credenciais nos seguintes arquivos: `scripts/db_conn.py` (SENHA), `scripts/integrar.py` (API_KEY). Elas foram substituidas por [REDACTED-*] nos arquivos texto, mas recomendo uma olhada antes de enviar."

### 5. Entregue o caminho ao usuario + proximos passos

Exemplo:

> "ZIP pronto: `C:/Users/fernando/workspace/202604_analise_vendas/shared/202604_analise_vendas_handoff_20260423.zip` (48.2 KB, 23 arquivos).
>
> Para enviar: anexe por email ou suba para Google Drive / Dropbox. O destinatario extrai, abre Claude Code na pasta e diz 'assumir projeto compartilhado'."

### 6. Registre no historico.md do projeto

```python
python -c "
from pmo_db import log_activity
log_activity('2026-04-23', '202604_analise_vendas-regiao', 'change', 'Projeto compartilhado via /compartilhar para Pedro', session_id=ID)
"
```

O `pmo_share.share_project()` JA faz log_activity automaticamente — so adicione no historico.md se quiser contexto adicional.

## Curadoria automatica

O `pmo_share.py` faz automaticamente:

**Exclui do ZIP:**
- `*.local.md`, `*.local.txt`, `*.local.json` (rascunhos pessoais)
- `.env`, `credentials.json`, `secrets.*`
- `__pycache__`, `*.pyc`
- `pmo.db*` (banco nao sai do workspace)
- Qualquer `.md` com frontmatter `sensitive: true`
- Intermediarios em `dados/` > 10MB que nao sejam `.md/.csv/.json`
- Pasta `shared/` (evita loop de shares)

**Scrub de texto:**
- `password=...`, `api_key=...`, `token=...`, `Bearer ...` → `[REDACTED-*]`
- Paths absolutos do workspace origem → `<WORKSPACE>`

**Gera novos:**
- `HANDOFF.md` — briefing para quem assume (o que e, estado atual, arquivos essenciais, pendencias)
- `RESUMO-EXECUTIVO.md` — panorama em 2 paginas
- `README-HANDOFF.txt` — "extraia, abra Claude Code, diga 'assumir projeto compartilhado'"

## Historico de melhoria

- v1 (2026-04-23): versao inicial com scrub basico + HANDOFF.md/RESUMO automaticos
