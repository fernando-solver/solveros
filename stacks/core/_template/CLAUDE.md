# Pasta de projeto (Solverkitty core)

Voce esta dentro de uma pasta de projeto. Esta pasta organiza tudo que
pertence a um trabalho, area de estudo, processo recorrente ou iniciativa
pessoal.

## Layout canonico

```
INDEX.md       <- canonicos (auto-gerado por pmo_index)
historico.md   <- append-only (atualizado por pmo_historico)
objetivos.md   <- objetivos especificos deste projeto
inbox/         <- drops humanos (arquivos que voce solta sem classificar)
saidas/        <- entregaveis finais consolidados
_archive/      <- versoes obsoletas (rotacao trimestral)
<sub-pastas>/  <- estrutura livre conforme o projeto pede
```

## Principios operacionais

1. **`INDEX.md` e fonte canonica.** Pergunta "onde esta o relatorio de
   maio?" responde abrindo INDEX, nao navegando arvore. Nao editar
   manualmente.
2. **`historico.md` e append-only.** Cronologico linear. Nunca reescrever
   passado.
3. **Drops humanos vao na `inbox/`.** Voce solta o arquivo ali, classifica
   na proxima sessao.
4. **Versoes obsoletas vao pra `_archive/<ano>Q<n>/`.** Nunca deletar sem
   archive primeiro.
5. **Cite fonte sempre.** Toda metrica, grafico, numero — referencia o
   arquivo de origem via `fonte_arquivo`.

## Proximo passo apos cadastro

Estruture sua pasta conforme o trabalho pede. Voce pode:
- **Comecar minimal** (so inbox/ + saidas/) e ir adicionando subpastas
  conforme o trabalho aparece
- **Aplicar um stack especializado** quando estiver disponivel
  (`/instalar-stack <nome>`) — stacks futuros vao trazer estrutura
  pronta pra ecommerce, consultorio, industria, etc
- **Criar subpastas manualmente** baseado no que faz sentido pra voce
