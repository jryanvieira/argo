# {{title}}

## Tarefa

{{task_description}}

## Critério de aceitação

{{acceptance_criteria}}

## Contexto

{{context}}

## Dicas para o acceptance.sh

- Use `grep -q "termo" harness/CLAUDE.md || exit 1` para verificar presença de instruções
- Use `[ -f harness/arquivo ]` para verificar existência de arquivos
- Retorne exit 0 para sucesso, exit 1 para falha

## Criado em

{{created_at}}
