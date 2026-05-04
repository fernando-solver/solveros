---
name: skill_exemplo_02_resumo-executivo
description: Gera resumo executivo de texto longo em 3 camadas (TL;DR, pontos-chave, acoes)
trigger: O usuario pede "resumo", "sumario" ou "TL;DR" de um documento, transcricao, email ou relatorio longo
version: 1
last_updated: 2026-04-22
uses_count: 0
---

# Resumo executivo em 3 camadas

## Quando usar

- Texto > 500 palavras que o usuario precisa absorver rapido
- Transcricao de reuniao, call, palestra
- Relatorio tecnico que um nao-especialista precisa entender
- Email longo que precisa virar acao

## Quando NAO usar

- Texto tecnico denso onde cada palavra importa (artigo cientifico, contrato juridico) — use sintese com citacoes diretas, nao resumo
- Texto de ficcao / literario — resumo destroi o ponto

## Procedimento

### Estrutura obrigatoria em 3 camadas

**Camada 1 — TL;DR (1 linha)**

Uma frase que substitui o documento inteiro se a pessoa so tiver 5 segundos.

Padroes que funcionam:
- "X aconteceu / decidiu / recomenda Y por causa de Z."
- "Status: N. Principal risco: M. Proximo passo: K."

**Camada 2 — Pontos-chave (3 a 7 bullets)**

Cada bullet e uma afirmacao completa, nao um topico. Evite:
- ❌ "Discussao sobre vendas"
- ✅ "Vendas caíram 15% em marco vs fevereiro por causa da saida do principal distribuidor"

**Camada 3 — Acoes / decisoes pendentes (se houver)**

Lista numerada de o-que-fazer com responsavel implicito ou explicito:
1. Renegociar contrato com fornecedor X (ate 30/abr)
2. Validar hipotese de canibalismo com dados do CRM
3. Decidir se repassa aumento de 8% ao consumidor (diretoria)

## Regras de qualidade

- **Sem jargao novo** — se o texto original tem termo tecnico, preserva; nao substitua por sinonimo pior.
- **Sem adjetivos decorativos** — "importante", "interessante", "grande" sao lixo.
- **Cada numero explicito** — se o texto diz "15%", diga "15%", nao "significativo".
- **Citacao direta quando a fonte disser algo forte** — entre aspas, com atribuicao se tiver.

## Exemplo de aplicacao

**Input:** transcricao de reuniao de 45 minutos (8.000 palavras) sobre queda de vendas no ecommerce.

**Output:**

```markdown
## TL;DR
Vendas do ecommerce caíram 22% em abril vs marco; causa principal e canibalismo do novo canal marketplace; decidimos pausar investimento em Meta Ads ate o dia 15/05 para testar a hipotese.

## Pontos-chave
- Queda de 22% em receita do ecommerce (abril vs marco)
- Crescimento de 31% no marketplace no mesmo periodo — volumes coincidem
- CAC no Meta Ads subiu 40% (R$ 78 → R$ 109)
- 67% dos novos clientes do marketplace ja haviam comprado no ecommerce
- Teste de pausa de Meta Ads em 2 regioes foi neutro — sugere canibalismo, nao dependencia de ads

## Acoes pendentes
1. Pausar 100% do orcamento Meta Ads em 15/05 por 14 dias (Joao)
2. Pull de dados cruzados ecommerce x marketplace em abril (Maria — prazo 25/04)
3. Decidir estrategia de precos diferenciados entre canais (diretoria — reuniao 10/05)
```

## Sinais de que precisa melhorar

- Se o usuario pedir "mais curto" consistentemente → reduzir default de pontos-chave de 7 para 3-5
- Se o usuario pedir "onde voce viu isso?" → adicionar paginação/timestamp de origem em textos longos
- Se o texto for audio transcrito → remover marcadores de fala ("eh", "ne", "entao")

## Historico de melhoria

- v1 (2026-04-22): versao inicial (exemplo do kit beta)
