# O Filesystem: Como Criar um Segundo Cerebro Corporativo

---

## A Verdade

Voce instalou o Claude Code achando que teria um assistente genial. E tem. Mas toda vez que abre uma sessao nova, ele acorda com amnesia completa. Nao sabe o que voce fez ontem. Nao sabe o que decidiu semana passada. Nao sabe que aquele script quebra se rodar sem o parametro `--dry-run`.

Voce perde 15 minutos explicando o contexto. Ele entende. Trabalha. Entrega. Voce fecha o terminal.

Amanha, tudo de novo. Do zero.

Isso nao e um problema do Claude. E um problema de arquitetura. Voce esta usando a ferramenta mais poderosa que ja existiu para trabalho intelectual — e tratando-a como um estagiario que voce demite e recontrata todo dia.

O filesystem resolve isso. Nao com prompts magicos. Com pastas.

---

## O Mecanismo

O Claude Code faz uma coisa que a maioria das pessoas ignora: ele le arquivos. Quando voce abre uma sessao dentro de uma pasta que tem um `CLAUDE.md`, ele le automaticamente. Quando voce pede para ele retomar um projeto e existe um `proximos-passos.md`, ele sabe exatamente onde parou.

O filesystem transforma a estrutura de pastas do seu computador num sistema nervoso. Cada pasta e um projeto. Cada projeto tem tres arquivos obrigatorios que dao memoria ao agente:

| Arquivo | Funcao | Analogia |
|---------|--------|----------|
| `CLAUDE.md` | O que esse projeto e, como funciona, quais sao as regras | **O briefing** — como explicar o projeto para um funcionario novo |
| `historico.md` | Tudo que ja foi feito, quando, e por que | **O diario** — a memoria de longo prazo |
| `proximos-passos.md` | Onde paramos, o que falta, o que ta travado | **O post-it no monitor** — a memoria de curto prazo |

O agente nao precisa de voce para lembrar. Ele abre a pasta, le os tres arquivos, e ja sabe: o que e o projeto, o que ja foi feito, e o que precisa fazer agora.

Sem esses arquivos, toda sessao comeca do zero.
Com esses arquivos, toda sessao comeca exatamente de onde parou.

---

## Os Tres Arquivos

### 1. CLAUDE.md — O Briefing

Imagine que voce contratou um consultor caro. Ele chega no escritorio e pergunta: "O que eu preciso saber sobre esse projeto?"

O `CLAUDE.md` e a resposta para essa pergunta.

Ele contem:
- **Contexto**: o que o projeto faz e por que existe
- **Arquivos importantes**: quais dados estao na pasta, de onde vieram, o que significam
- **Regras**: limites, excecoes, cuidados especificos
- **Comandos**: acoes predefinidas que o agente pode executar

Exemplo real:

```markdown
# Curadoria Mensal de Newsletter

## Contexto
Newsletter pessoal que sai toda primeira segunda do mes.
Baseada em artigos lidos durante o mes — preciso gerar resumos curados.
Enviada por email para a lista de assinantes.

## Arquivos importantes
- gerar_newsletter.py: pipeline principal (le pasta de PDFs -> HTML)
- enviar.py: integracao com SMTP (credenciais no .env)

## Regras
- Apenas PDFs lidos no mes corrente (filtrar por data de modificacao)
- Tom editorial, nao academico
- Maximo 8 itens, mesmo que tenha lido mais

## Comandos
### /gerar
Le a pasta de PDFs do mes e gera o HTML da newsletter.
### /enviar
Envia para a lista de assinantes.
```

O agente le isso e sabe tudo que precisa. Sem perguntas. Sem contexto perdido. Sem "me explica de novo o que era esse projeto".

---

#### Ingenuo vs Blindado: O Briefing

```
INGENUO                                  BLINDADO

Abre o Claude Code e digita:             Abre o Claude Code dentro da pasta
"me ajuda com aquela newsletter,         do projeto. O CLAUDE.md e lido
sabe? aquela que eu mando todo           automaticamente. O agente ja sabe:
mes, com resumo dos artigos              qual script rodar, quais PDFs
que eu li..."                            considerar, quantos itens incluir,
                                         qual o tom editorial.

O agente: "Pode me dar mais              O agente: "Vou gerar a newsletter
detalhes sobre essa newsletter?"         do mes. Lendo PDFs lidos em maio,
                                         filtrando por data de modificacao,
15 minutos explicando contexto.          maximo 8 itens, tom editorial..."

                                         0 minutos explicando contexto.
```

---

### 2. historico.md — O Diario

O `historico.md` e o registro cronologico de tudo que aconteceu no projeto. Nao e para voce ler todo dia. E para o agente consultar quando precisa entender uma decisao do passado.

Por que isso importa? Porque projetos reais tem historia. Voce tentou uma abordagem, nao funcionou, mudou. Essa informacao e ouro. Sem ela, o agente pode sugerir exatamente a abordagem que ja falhou.

Formato:

```markdown
# Historico - Newsletter Mensal

## 2026-04-07
- [feature] Pipeline criado com 3 etapas: leitura PDFs, sumarizacao, montagem HTML
- [decision] Usar tom editorial conversacional em vez de academico
- [discovery] Em meses com >10 artigos, qualidade do resumo cai — limitei a 8

## 2026-04-03
- [config] Configuracao SMTP centralizada em .env (nao versionado)
- [bugfix] Encoding UTF-8 quebrava emojis no titulo do email — corrigido
```

Cada entrada tem um **tipo** entre colchetes. Isso nao e burocracia — e filtragem. Quando o agente precisa entender por que algo e do jeito que e, ele busca entradas do tipo `decision`. Quando precisa saber o que quebrou no passado, busca `bugfix`.

| Tipo | Quando usar |
|------|-------------|
| `decision` | Escolha que afeta o rumo do projeto |
| `bugfix` | Correcao de erro |
| `feature` | Funcionalidade nova criada |
| `discovery` | Achado importante nos dados ou no processo |
| `refactor` | Reorganizacao sem mudar funcionalidade |
| `config` | Configuracao de ambiente ou ferramenta |
| `analysis` | Resultado de uma analise |
| `change` | Alteracao que nao se encaixa nos anteriores |

---

#### Ingenuo vs Blindado: O Historico

```
INGENUO                                  BLINDADO

Sessao 1: "Faz um relatorio              Sessao 1: Agente cria pipeline,
de vendas semanal."                      registra no historico.md:
Agente cria o pipeline.                  "[decision] Comparativo YoY
                                         escolhido porque MoM distorce
Sessao 5: "Por que o relatorio           por sazonalidade"
compara com o ano passado e
nao com o mes passado?"                  Sessao 5: Agente le o historico
                                         e ja sabe a resposta. Nao precisa
"...nao lembro, acho que fazia           perguntar. Nao precisa adivinhar.
mais sentido."                           A decisao esta documentada com
                                         o motivo.
Resultado: retrabalho, duvida,
risco de desfazer algo que               Resultado: continuidade perfeita.
funcionava.                              O projeto tem memoria.
```

---

### 3. proximos-passos.md — O Post-it

Esse e o arquivo mais subestimado e o mais importante para a operacao do dia a dia.

O `historico.md` conta o que ja aconteceu. O `proximos-passos.md` conta o que precisa acontecer. E a diferenca entre um agente que precisa ler 200 linhas de historico para entender o estado atual e um que abre 1 arquivo e ja sabe:

- O que esta funcionando
- O que esta pendente (e a prioridade)
- O que esta travado (e por que)
- Quais bugs sao conhecidos

Formato:

```markdown
# Proximos Passos

## Situacao atual
Pipeline funcionando. Relatorio da semana 14 gerado e enviado.
Diretoria pediu para adicionar grafico de novos clientes.

## Acoes pendentes
1. [PRIORIDADE] Adicionar bloco "Novos Clientes" ao relatorio
2. [PRIORIDADE] Automatizar envio toda segunda as 8h (RemoteTrigger)
3. [NORMAL] Adicionar filtro por departamento
4. [FUTURO] Criar versao executiva resumida (1 pagina)

## Dependencias
- Dados de abril so disponiveis apos dia 5

## Bugs conhecidos
- Grafico de rentabilidade nao renderiza se nao houver vendas no periodo
```

**Regra critica:** atualize esse arquivo ao FINAL de cada sessao. Se voce nao atualizar, a proxima sessao comeca cega. E como sair do escritorio sem deixar anotado onde parou.

---

#### Ingenuo vs Blindado: A Retomada

```
INGENUO                                  BLINDADO

Segunda-feira. Abre o Claude Code.       Segunda-feira. Abre o Claude Code.
"Oi, entao, semana passada a gente       Agente le proximos-passos.md.
tava mexendo no relatorio, eu acho
que faltava... deixa eu pensar...        "Bom dia. Retomando de onde
a diretoria pediu uma coisa..."          paramos: o pipeline esta
                                         funcionando, o relatorio da
Gasta 10 minutos reconstruindo           semana 14 foi enviado. A
o contexto mentalmente.                  prioridade e adicionar o bloco
                                         de Novos Clientes que a diretoria
Agente comeca a trabalhar                pediu. Posso comecar?"
baseado em informacao incompleta.
                                         0 minutos de contexto.
Resultado: erros, retrabalho,            Resultado: execucao imediata,
frustacao.                               foco no que importa.
```

---

## A Pasta: Anatomia de um Projeto

Cada projeto e uma pasta no seu computador, dentro da pasta do departamento. O caminho segue um padrao rigido:

```
_departamento/AAAAMM_empresa_nome-do-projeto
```

- `_departamento` = pasta de topo por area funcional, com prefixo `_` (ex: `_financeiro`, `_credito`, `_fiscal`). O `_` mantem os departamentos no topo da listagem.
- `AAAAMM` = ano e mes de criacao (ex: 202605)
- `empresa` = empresa do grupo a que o projeto pertence (ex: jandaia)
- `nome-do-projeto` = descricao curta com hifens, minuscula

Exemplos:
- `_financeiro/202605_jandaia_conciliacao-bancaria`
- `_credito/202605_jandaia_analise-inadimplencia`
- `_fiscal/202605_empresa-b_apuracao-icms`

Esse padrao nao e estetica. E funcionalidade. Alem disso, `empresa` e `departamento` viram campos no banco (pmo.db) — entao da pra cruzar "tudo da empresa X" ou "todas as conciliacoes do grupo" por query. A arvore de pastas e pra leitura humana; o agente raciocina pelo banco.

Estrutura interna:

```
_financeiro/202605_jandaia_conciliacao-bancaria/
  CLAUDE.md              -- briefing (obrigatorio)
  historico.md           -- diario (obrigatorio)
  proximos-passos.md     -- retomada (obrigatorio)
  dados/                 -- arquivos intermediarios
  scripts/               -- codigo Python
  saidas/                -- entregas finais (HTML, XLSX)
```

A pasta 000000 e especial: fica sempre no topo da listagem. E reservada para o PMO — relatorios gerenciais, consolidacoes, templates. E a "sala da diretoria" do seu workspace.

---

## O Banco: pmo.db

Os tres arquivos dao memoria ao projeto individual. O banco SQLite (`pmo.db`) da memoria ao workspace inteiro.

Toda sessao de trabalho e registrada. Toda atividade importante e logada. Toda pendencia e rastreada. Isso permite perguntas que nenhum arquivo .md consegue responder:

- "Quais projetos nao tem atividade ha 30 dias?" → `inactive_projects(30)`
- "O que foi feito ontem em todos os projetos?" → `query_activities('date = ?', ('2026-04-11',))`
- "Quais pendencias estao abertas?" → `list_pending()`

O banco nao substitui os arquivos .md. Ele complementa. Os .md sao leitura — o agente abre e entende. O banco e consulta — o agente roda queries e responde perguntas transversais.

---

## O Protocolo de Sessao

Todo o sistema se conecta por um protocolo simples que roda em toda sessao de trabalho:

```
INICIO
  |
  v
[1] Registrar sessao no banco (session_start)
  |
  v
[2] Ler proximos-passos.md do projeto
  |    (se nao existir, ler historico.md)
  |    (se nao existir, ler CLAUDE.md)
  |
  v
[3] Trabalhar
  |    A cada marco: registrar no banco (log_activity)
  |
  v
[4] Atualizar historico.md com o que foi feito
  |
  v
[5] Atualizar proximos-passos.md com novo estado
  |
  v
[6] Encerrar sessao no banco (session_end)
  |
  v
FIM
```

Esse protocolo e o que transforma um assistente de IA em um operador autonomo. Ele nao precisa de voce para lembrar. Ele nao precisa de voce para registrar. Ele opera, documenta, e deixa tudo pronto para a proxima sessao — seja voce, outro humano, ou outro agente.

---

## A Arquitetura: PMO + Subagentes

Ate aqui voce entendeu como um projeto funciona. Agora vem a parte que muda tudo: como dezenas de projetos funcionam juntos sem virar caos.

A pasta raiz do workspace nao e apenas uma colecao de pastas. Ela e o **PMO** — o agente gestor. Quando voce abre o Claude Code na raiz, ele le o CLAUDE.md principal e assume o papel de COO: entende todos os projetos, sabe o que esta ativo, o que esta atrasado, o que precisa de atencao.

Mas o PMO nao executa o trabalho dos projetos. Ele **spawna subagentes**.

### Por que subagentes?

Porque contexto misturado e contexto poluido.

Se o agente PMO entra numa pasta de analise de vendas, comeca a ler planilhas, rodar queries, gerar graficos — ele perde a visao estrategica. O contexto do projeto invade o contexto de gestao. Na proxima pergunta sobre prioridades, ele esta pensando em SQL em vez de pensar em estrategia.

A solucao e cirurgica: o PMO spawna um subagente dentro da pasta do projeto. O subagente nasce com contexto limpo, le o CLAUDE.md daquele projeto, executa o trabalho, registra no historico.md, atualiza o proximos-passos.md, e morre. O PMO continua intacto.

```
WORKSPACE (DATA2)
  |
  |-- CLAUDE.md  ← PMO le isso. Assume papel de COO.
  |-- pmo.db     ← Banco central. Memoria de tudo.
  |
  |-- 202604_analise_vendas/
  |     |-- CLAUDE.md  ← Subagente le isso. Sabe o que fazer.
  |     |-- historico.md
  |     |-- proximos-passos.md
  |
  |-- 202604_mkt_carrinho/
  |     |-- CLAUDE.md  ← Outro subagente, outro contexto.
  |     |-- historico.md
  |     |-- proximos-passos.md
  |
  |-- 202603_cad_dimensoes/
        |-- CLAUDE.md  ← Mais um. Todos independentes.
        |-- historico.md
        |-- proximos-passos.md
```

O resultado: voce tem um gestor na raiz com visao panoramica e dezenas de especialistas trabalhando em paralelo, cada um com contexto perfeito do seu projeto. Nenhum interfere no outro.

### Ingenuo vs Blindado: Gestao de Contexto

```
INGENUO                                  BLINDADO

Abre o Claude Code na raiz.              Abre o Claude Code na raiz.
"Analisa as vendas da semana,            "Spawna um subagente na pasta
depois cria os sliders de                202604_analise_vendas para gerar
promocao, depois verifica as             o relatorio semanal."
tarefas atrasadas no Asana."
                                         O subagente nasce, le o CLAUDE.md
O agente tenta fazer tudo no             da pasta, executa, registra,
mesmo contexto. Na terceira              e retorna o resultado.
tarefa ja esqueceu detalhes
da primeira. Mistura dados               PMO continua limpo. Spawna outro
de vendas com assets de                  subagente para os sliders.
marketing. Confunde filtros.             Depois outro para o Asana.

Resultado: erros cruzados,               Resultado: cada tarefa executada
contexto poluido, retrabalho.            com contexto isolado e perfeito.
                                         PMO mantem visao estrategica.
```

### A hierarquia na pratica

O dia a dia funciona assim:

1. **Voce** abre o Claude Code na raiz e fala com o PMO
2. O PMO consulta o banco (`pmo.db`), ve o que esta pendente, o que esta atrasado
3. Voce decide a prioridade: "hoje vamos focar no relatorio semanal"
4. O PMO **spawna um subagente** na pasta do relatorio
5. O subagente le os tres arquivos, executa, documenta, e retorna
6. O PMO registra a atividade no banco central
7. Se algo precisa ser feito por um humano, o PMO **cria uma tarefa no Asana**
8. Proximo projeto. Spawna outro subagente. Repete.

Voce nao e um operador. Voce e um diretor dando ordens a um COO que tem uma equipe ilimitada de especialistas.

---

## A Escala: Do Subagente ao Time Humano

Ate aqui voce tem um sistema poderoso: PMO na raiz, subagentes nas pastas, contexto isolado, execucao perfeita. Mas tudo isso ainda e maquina falando com maquina.

E quando o trabalho precisa de maos humanas?

O filesystem sozinho nao resolve isso. Ele da contexto ao agente, mas nao distribui trabalho para humanos. Nao cobra prazos. Nao rastreia quem fez o que.

Para isso, existe uma segunda camada: **Asana**.

### Filesystem + Asana = Segundo Cerebro Corporativo

| Camada | Ferramenta | Funcao |
|--------|-----------|--------|
| Contexto | Filesystem (CLAUDE.md, historico.md, proximos-passos.md) | O agente sabe o que fazer |
| Execucao | pmo.db + scripts Python | O agente faz o trabalho |
| Gestao | Asana (projetos, tarefas, subtarefas, responsaveis) | O agente delega e cobra |

O fluxo na pratica:

1. O agente le o filesystem e entende o projeto
2. Identifica o que precisa ser feito por humanos
3. Cria tarefas no Asana com responsavel, prazo e descricao
4. Monitora execucao (tarefas atrasadas, pendencias)
5. Cobra via comentario ou alerta
6. Registra progresso no filesystem

O resultado: um COO digital que nao esquece, nao deixa passar, e nao precisa que voce fique cobrando a equipe manualmente.

### Ingenuo vs Blindado: Gestao de Time

```
INGENUO                                  BLINDADO

Manda mensagem no WhatsApp:              Agente cria tarefa no Asana:
"Oi Pedro, tudo bem? Quando              "Cupom desconto automatico
voce puder dar uma olhada                Responsavel: Pedro
naquele cupom de desconto..."            Prazo: 25/04
                                         Descricao: [Objetivo + Por que
Pedro visualiza. Esquece.                + Entregavel + Atencao]"
Fernando esquece que pediu.
3 meses depois: "Ah, aquilo              Agente verifica semanalmente:
do cupom, como ficou?"                   "Pedro tem 3 tarefas atrasadas.
                                         Comentando no Asana para
Resultado: nada foi feito.               visibilidade do time."
Ninguem cobrou. Ninguem
lembrou. Zero rastreabilidade.           Resultado: tudo documentado,
                                         rastreavel, com historico
                                         de cobrancas.
```

### A Ponte entre Agentes: Asana como Area de Transferencia

Aqui e onde a coisa fica realmente interessante.

Imagine que o Pedro, da TI, tambem tem Claude Code. Ele tem seu proprio workspace, seu proprio CLAUDE.md, seus proprios projetos. O agente dele entende o contexto do Pedro.

Agora imagine que o seu PMO cria uma tarefa no Asana para o Pedro: "Integrar cupom de desconto automatico. Prazo: 25/04." Com descricao detalhada, objetivo, entregavel.

O Pedro abre o Claude Code dele. O agente do Pedro le o Asana. Ve a tarefa. Entende o que precisa fazer. Executa. Atualiza a tarefa no Asana com o resultado.

O seu PMO, na proxima verificacao, ve que a tarefa foi concluida. Registra no banco. Atualiza o historico.

O que aconteceu? **Dois agentes de IA, sob comando de dois humanos diferentes, trocaram conhecimento e coordenaram trabalho atraves do Asana.**

Nenhum dos dois agentes se falou diretamente. Nao precisou. O Asana e a area de transferencia. A tarefa e o pacote de informacao. O humano e o validador.

```
SEU WORKSPACE                    ASANA                    WORKSPACE DO PEDRO
                                  
PMO (raiz)                        |                       PMO do Pedro
  |                               |                         |
  |-- spawna subagente            |                         |
  |     |                         |                         |
  |     |-- identifica            |                         |
  |     |   necessidade      cria tarefa ──────►  tarefa    |
  |     |   humana                |              aparece    |
  |     |                         |                  |      |
  |     |                         |            agente do    |
  |     |                         |            Pedro le     |
  |     |                         |            e executa    |
  |     |                         |                  |      |
  |     |                    tarefa ◄────── atualiza tarefa |
  |     |                   concluida          resultado    |
  |     |                         |                         |
  |-- PMO verifica                |                         |
  |   e registra                  |                         |
```

Isso nao e ficcao cientifica. Isso ja funciona. Hoje.

### O que o Obsidian nao faz

O Obsidian te ajuda a organizar pensamentos. E otimo para isso. Mas ele:

- Nao executa codigo
- Nao conecta com banco de dados
- Nao cria tarefas para outras pessoas
- Nao monitora prazos
- Nao envia emails
- Nao cobra a equipe
- Nao spawna subagentes
- Nao coordena trabalho entre agentes de pessoas diferentes

O filesystem do Claude Code faz tudo isso. E quando conectado ao Asana, ele nao organiza apenas as suas ideias — ele **gestiona o trabalho de um time inteiro**.

A diferenca entre um segundo cerebro pessoal e um segundo cerebro corporativo e simples: o pessoal te ajuda a pensar. O corporativo pensa, executa, delega, cobra, e **coordena outros agentes atraves de humanos**.

---

## Resumo

Se voce levar uma coisa deste guia, leve isso:

**Tres arquivos. Uma pasta por projeto. Um banco na raiz.**

```
MEU_WORKSPACE/
  CLAUDE.md                    -- instrucoes gerais do workspace
  pmo.db                       -- banco SQLite (memoria central)
  pmo_db.py                    -- funcoes de acesso ao banco
  GLOSSARIO.md                 -- indice de todos os projetos
  DIARIO.md                    -- registro diario consolidado
  000000_pmo_consolidacao/     -- pasta PMO (sempre no topo)
  202604_analise_meu-projeto/  -- seu primeiro projeto
    CLAUDE.md                  -- briefing do projeto
    historico.md               -- o que ja foi feito
    proximos-passos.md         -- o que falta fazer
```

Copie essa estrutura. Preencha o CLAUDE.md com o contexto do seu trabalho. Comece a usar. Em uma semana voce nao volta atras.

O agente para de ser um estagiario amnesico e vira um operador com memoria perfeita.
