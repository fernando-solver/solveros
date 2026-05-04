# inbox/

**Funcao:** porta de entrada de drops humanos.

## O que vai aqui

Qualquer arquivo que o dono (ou equipe, ou parceiro) joga sem saber onde catalogar:

- Planilhas, exports, relatorios
- Atas de reuniao em PDF
- Imagens, screenshots, documentos
- Anotacoes manuscritas escaneadas

## Como funciona a classificacao

`pmo_inbox.propose_classifications(slug)` le tudo aqui e classifica baseado em:

1. **Padrao no nome** — regex configuravel por stack
2. **Inferencia por header** (XLSX) — se ativada
3. **Conteudo de ZIP** — se ativada
4. **Fallback por extensao** — `.pdf` -> primeiro depto, `.csv` -> dados, etc.

`apply_classification(slug, basename, departamento)` move pro destino certo.

## NAO

- Nao usar inbox como armazenamento permanente. Tudo aqui e transitorio.
- Nao mover arquivo manualmente da inbox sem registrar — quebra rastreabilidade.
