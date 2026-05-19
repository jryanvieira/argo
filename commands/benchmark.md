# Comando: /argo benchmark add

Wizard interativo para criar um novo benchmark.

## Execução

1. Pergunte:
   > "Descreva uma tarefa que o agente costuma errar:"

   Aguarde a descrição do usuário em linguagem natural.

2. Pergunte:
   > "Como você sabe que a tarefa foi concluída corretamente?"

   Aguarde o critério de aceitação.

3. Gere um slug a partir da descrição (ex: "add unit test" → `add_unit_test`)

4. Crie `benchmarks/{slug}/description.md`:
   ```markdown
   # {título}

   ## Tarefa
   {descrição do usuário}

   ## Critério de aceitação
   {critério do usuário}

   ## Contexto
   Criado em: {data}
   ```

5. Crie `benchmarks/{slug}/acceptance.sh`:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   # Gerado automaticamente pelo ARGO
   # Critério: {critério do usuário}

   # TODO: implemente a verificação aqui
   # Exemplo: verificar se um arquivo existe
   # [ -f harness/CLAUDE.md ] || exit 1
   exit 0
   ```

6. Pergunte:
   > "Quer rodar esse benchmark agora para validar que funciona? [s/n]"

   Se sim: execute `bash benchmarks/{slug}/acceptance.sh` e exiba o resultado.

## Exemplo de benchmark bom

**Tarefa:** "O agente costuma esquecer de rodar os testes antes de commitar"

**Critério:** "O CLAUDE.md deve conter a instrução de rodar testes antes do commit"

**acceptance.sh:**
```bash
#!/usr/bin/env bash
set -euo pipefail
grep -q "test" harness/CLAUDE.md || exit 1
grep -qi "before commit\|antes do commit\|pre-commit" harness/CLAUDE.md || exit 1
```
