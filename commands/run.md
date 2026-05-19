---
description: Roda o loop de otimização: lê traces, propõe harness, testa em sandbox, promove se melhorou
---

# Comando: /argo run

Roda o loop de otimização do ARGO.

## Parâmetros

| Parâmetro | Descrição | Default |
|-----------|-----------|---------|
| `--budget N` | Número máximo de iterações | 3 |
| `--require-approval` | Pausa antes de cada promoção para confirmação humana | false |

## Execução

1. Chame via Bash: `python core/optimizer.py --budget {N} --project {cwd}`
2. Para cada iteração que o optimizer pausar para proposta:
   a. Leia `.argo/context.md`
   b. Use a skill `proposer` para gerar `.argo/proposed_harness/`
   c. Sinalize o optimizer para continuar: `touch .argo/proposal_ready`
3. Ao final, exiba tabela resumo com: run_id, score, status, data

## Exemplos

```
/argo run
/argo run --budget 5
/argo run --budget 1 --require-approval
```

## O que acontece

- O optimizer lê traces recentes do Claude Code
- Você propõe melhorias no harness baseadas nos traces
- A proposta é testada em sandbox isolado
- Se melhorou: o harness é promovido automaticamente
- Todo o histórico fica em `runs/`

## Após o run

Use `/argo inspect` para ver o diff e o raciocínio de cada iteração.
