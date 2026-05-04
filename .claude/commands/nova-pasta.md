---
description: Criar nova pasta de projeto com estrutura padrao
argument-hint: [nome-projeto] [categoria] [descricao]
---

Execute o comando `/nova-pasta` conforme a secao "## /nova-pasta" do CLAUDE.md na raiz.

Fluxo:

1. Se o usuario nao forneceu os 3 argumentos, **pergunte um de cada vez**:
   - Nome do projeto (minusculo, hifens: ex `analise-vendas`)
   - Categoria (ver categorias definidas em CLAUDE.md)
   - Descricao curta (1 linha)

2. Execute via Bash:

```bash
python -c "from pmo_setup import nova_pasta; nova_pasta('<nome>', '<categoria>', '<descricao>')"
```

3. Confirme ao usuario: pasta criada, banco atualizado, GLOSSARIO.md atualizado, `shared/` criado.

4. Pergunte se o usuario ja quer comecar a trabalhar no projeto (abrir `01_input/instrucoes.md` para preencher fonte de dados).

Argumentos recebidos: $ARGUMENTS
