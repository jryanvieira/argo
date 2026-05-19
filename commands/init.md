# Comando: /argo init

Inicializa o ARGO num projeto.

## Parâmetros

| Parâmetro | Descrição |
|-----------|-----------|
| `[nome]` | Nome opcional do projeto (default: nome da pasta atual) |

## Execução

1. Crie a estrutura de diretórios no projeto atual:
   ```
   harness/        ← CLAUDE.md e scripts do projeto
   benchmarks/     ← tarefas com acceptance.sh
   runs/           ← histórico de otimizações
   .argo/          ← estado interno do loop
   ```

2. Gere `harness/CLAUDE.md` a partir de `templates/CLAUDE.md.tpl`:
   - Detecte a linguagem principal (procure por go.mod, package.json, requirements.txt, etc.)
   - Detecte a estrutura do projeto (src/, cmd/, tests/, etc.)
   - Detecte ferramentas disponíveis (make, pytest, go test, npm test, etc.)
   - Personalize o template com essas informações

3. Gere `benchmarks/example_task/` com:
   - `description.md` — tarefa de exemplo funcional
   - `acceptance.sh` — critério de aceitação como script bash

4. Exiba próximos passos:
   ```
   ARGO inicializado em: {nome}

   Próximos passos:
   1. Edite harness/CLAUDE.md com suas regras reais
   2. Adicione benchmarks do seu trabalho: /argo benchmark add
   3. Rode a primeira otimização: /argo run --budget 3
   ```

## Exemplo

```
/argo init meu-api
```
