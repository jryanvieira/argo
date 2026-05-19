# Arquitetura do ARGO

## Visão geral

```
┌─────────────────────────────────────────────────────┐
│                   Claude Code                        │
│  (runtime, propositor, executor de ferramentas)      │
│                                                      │
│   /argo run ──► commands/run.md                      │
│                     │                                │
│                     ▼                                │
│            skills/optimizer.md                       │
│                     │                                │
│         ┌───────────┴───────────┐                    │
│         ▼                       ▼                    │
│   skills/tracer.md        skills/proposer.md         │
└────────────────────────────────┬────────────────────┘
                                 │ filesystem
                    ┌────────────┴────────────┐
                    ▼                         ▼
             .argo/context.md     .argo/proposed_harness/
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    ┌────────────────────────┐
                    │    core/optimizer.py   │ ◄── Python puro, stdlib
                    │  (loop de controle)    │
                    └────────────────────────┘
                         │           │
                    ┌────┘           └────┐
                    ▼                     ▼
             core/sandbox.py       core/store.py
             (tmpdir isolado)      (runs/ filesystem)
```

## Separação de responsabilidades

| Componente | Responsabilidade | Tecnologia |
|-----------|-----------------|-----------|
| Claude Code | Propor harnesses melhores | LLM interno |
| `core/optimizer.py` | Orquestrar o loop | Python stdlib |
| `core/tracer.py` | Extrair sinais de falha | Python stdlib |
| `core/sandbox.py` | Testar propostas em isolamento | Python + bash |
| `core/store.py` | Persistir runs | Python stdlib |
| `skills/` | Ensinar o Claude Code a executar cada etapa | Markdown |
| `commands/` | Definir a interface do usuário | Markdown |

## Fluxo de dados

1. **Claude Code usa o projeto** → traces salvos em `~/.claude/projects/**/*.jsonl`
2. **`/argo run`** → invoca `core/optimizer.py`
3. **optimizer** → lê traces via `core/tracer.py` → escreve `.argo/context.md`
4. **Claude Code** → lê `context.md` → usa skill `proposer` → escreve `.argo/proposed_harness/`
5. **optimizer** → detecta `proposal_ready` → valida escopo → testa em sandbox
6. **sandbox** → executa `benchmarks/*/acceptance.sh` em tmpdir isolado → retorna score
7. **store** → salva artefatos em `runs/run_NNN/`
8. **optimizer** → se score melhorou: substitui `harness/` pela proposta

## Por que sem API key?

O Claude Code **já tem acesso ao modelo** internamente. O ARGO usa o Claude Code como runtime,
não como biblioteca. Nenhum código Python chama a API diretamente.

O Python só prepara contexto, executa scripts bash e gerencia o filesystem.
O LLM é invocado implicitamente quando o Claude Code lê o context.md e usa as skills.

## Persistência entre sessões

O estado do ARGO é 100% filesystem:

```
projeto/
├── harness/           ← harness atual (promovido se melhorou)
├── runs/              ← histórico imutável de todas as iterações
├── benchmarks/        ← testes que definem "bom harness"
└── .argo/             ← estado temporário da iteração em curso
```

Isso significa que o ARGO funciona mesmo se o Claude Code reiniciar — o estado
persiste entre sessões sem necessidade de banco de dados ou serviço externo.
