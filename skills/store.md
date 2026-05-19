# Skill: store

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

## Como usar via Python

```python
from core.store import Store, RunResult

store = Store("/caminho/do/projeto")

# Carregar histórico
runs = store.carregar_runs()

# Melhor score atual (apenas runs com status 'keep')
melhor = store.melhor_score_atual()

# Próximo ID disponível
run_id = store.proximo_run_id()

# Salvar run
resultado = RunResult(score=0.85, status="keep")
store.salvar_run(run_id=run_id, resultado=resultado, diff="...", reasoning="...")
```

## Convenções

- IDs são zero-padded (`run_001`, `run_002`, ...)
- Timestamps em ISO 8601 UTC
- Scores são floats entre 0.0 e 1.0
