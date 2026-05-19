# ARGO — Agent Runtime Goal Optimizer

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)

**ARGO otimiza harnesses de coding agents automaticamente.**

Zero API key. Zero pip install obrigatório. Funciona como plugin do Claude Code.

---

## Quickstart

```bash
# 1. instala o plugin
/plugin add github.com/seu-user/argo

# 2. inicializa num projeto
/argo init

# 3. roda o loop de otimização
/argo run --budget 3
```

---

## Como funciona

```
sessão 1: você usa Claude Code normalmente
               ↓ traces salvos em ~/.claude/projects/
sessão 2: /argo run
               ↓ lê traces de falha
               ↓ Claude Code propõe novo harness
               ↓ testa em sandbox isolado
               ↓ promove se melhorou
sessão 3: Claude Code começa com harness melhorado
```

O loop roda **dentro** do Claude Code, mas o estado persiste **fora** dele
no filesystem. Cada sessão é melhor que a anterior.

---

## Comandos disponíveis

| Comando | Descrição |
|---------|-----------|
| `/argo init` | Inicializa ARGO no projeto atual |
| `/argo run --budget N` | Roda N iterações de otimização |
| `/argo logs` | Analisa traces e lista padrões de falha |
| `/argo benchmark add` | Wizard para criar um benchmark |
| `/argo inspect [id]` | Inspeciona histórico de runs |

---

## Por que ARGO?

| Feature | ARGO | Outros frameworks |
|---------|------|-------------------|
| API key necessária | ✗ | ✓ (maioria) |
| pip install | ✗ (stdlib only) | ✓ |
| Funciona offline | ✓ | ✗ |
| Aprende com traces reais | ✓ | ✗ |
| Sandbox automático | ✓ | ✗ |

---

## Estrutura do projeto

```
argo/
├── commands/    ← /argo init, run, inspect, logs, benchmark
├── skills/      ← optimizer, tracer, sandbox, store, proposer
├── core/        ← Python stdlib: optimizer, tracer, sandbox, store, benchmark
├── templates/   ← CLAUDE.md.tpl, acceptance.sh.tpl
├── tests/       ← pytest, 36 testes
└── docs/        ← conceitos, arquitetura, onboarding, benchmarks, backends
```

---

## Documentação

- [Conceitos](docs/01-conceitos.md) — harness, loop, trace, benchmark
- [Arquitetura](docs/02-arquitetura.md) — como os componentes se conectam
- [Onboarding](docs/03-onboarding.md) — primeiro run passo a passo
- [Benchmarks](docs/04-benchmarks.md) — como criar testes eficazes
- [Backends](docs/05-backends.md) — como adicionar Ollama, Claude API, etc.

---

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

[Apache 2.0](LICENSE)
