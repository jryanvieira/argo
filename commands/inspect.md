# Comando: /argo inspect

Inspeciona o histórico de runs do ARGO.

## Parâmetros

| Parâmetro | Descrição |
|-----------|-----------|
| `[run_id]` | ID do run específico (ex: 0, 1, 42) — opcional |

## Sem run_id

Exibe tabela de todos os runs:

```
ID     Score    Status             Data
----------------------------------------------
000    0.0%     no-change          2026-05-19
001    75.0%    keep               2026-05-19
002    60.0%    discard            2026-05-20
003    100.0%   keep               2026-05-20
```

## Com run_id

Exibe detalhes completos do run:

1. Leia `runs/run_{id:03d}/meta.json` — metadata geral
2. Leia `runs/run_{id:03d}/REASONING.md` — raciocínio do propositor
3. Leia `runs/run_{id:03d}/diff.patch` — diff colorido do harness
4. Leia `runs/run_{id:03d}/result.json` — score por benchmark
5. Leia `runs/run_{id:03d}/traces_usados.json` — traces que embasaram a proposta

Exiba na ordem: metadata → reasoning → diff → benchmarks → traces.

## Exemplos

```
/argo inspect
/argo inspect 3
```
