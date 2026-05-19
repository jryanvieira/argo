---
description: Salva e carrega runs do filesystem do ARGO em runs/run_NNN/
---

Você sabe como salvar e carregar runs do filesystem do ARGO.

## Estrutura de um run

Cada run fica em `runs/run_NNN/`:

```
runs/run_001/
├── proposed_harness/     ← cópia dos arquivos propostos
├── traces_usados.json    ← traces que embasaram a proposta
├── diff.patch            ← diff entre harness atual e proposta
├── result.json           ← score, status, tempo por benchmark
├── meta.json             ← timestamp, budget, run_id, modelo
└── REASONING.md          ← raciocínio do propositor
```

## Status possíveis

| Status | Significado |
|--------|-------------|
| `keep` | Promovido — melhorou o score |
| `discard` | Não melhorou — descartado |
| `crash` | Benchmark crashou ou deu timeout |
| `timeout` | Propositor não respondeu a tempo |
| `no-change` | Propositor não encontrou o que mudar |
| `scope-violation` | Proposta tentou modificar arquivos fora de harness/ |

## Convenções

- IDs são zero-padded (`run_001`, `run_002`, ...)
- Timestamps em ISO 8601 UTC
- Scores são floats entre 0.0 e 1.0
