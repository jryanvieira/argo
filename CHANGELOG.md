# Changelog

Todas as mudanças notáveis neste projeto são documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [0.1.0] — 2026-05-19

### Adicionado

- Loop central de otimização (`core/optimizer.py`) com suporte a budget e require-approval
- Store de runs no filesystem (`core/store.py`) — persiste artefatos em `runs/run_NNN/`
- Tracer de sessões do Claude Code (`core/tracer.py`) — lê JSONLs e extrai sinais de falha
- Sandbox isolado (`core/sandbox.py`) — testa propostas em tmpdir sem tocar o workspace
- Executor de benchmarks (`core/benchmark.py`) — roda acceptance.sh e retorna score
- 5 skills: `optimizer`, `tracer`, `sandbox`, `store`, `proposer`
- 5 comandos: `/argo init`, `/argo run`, `/argo inspect`, `/argo logs`, `/argo benchmark add`
- Templates: `CLAUDE.md.tpl`, `description.md.tpl`, `acceptance.sh.tpl`
- 36 testes cobrindo todos os módulos core
- Documentação completa em `docs/` (conceitos, arquitetura, onboarding, benchmarks, backends)
- `scripts/install.sh` para verificação de dependências
- `plugin.yaml` com manifesto completo

### Status de sinais detectados pelo tracer

- Sessões com mais de 8 turnos
- Mesmo comando bash repetido 3+ vezes seguidas
- Mensagens curtas de correção do usuário após erros

### Status possíveis de runs

`keep` | `discard` | `crash` | `timeout` | `no-change` | `scope-violation`
