# Onboarding — Primeiro run passo a passo

## Pré-requisitos

- Claude Code instalado
- Python 3.10+
- bash disponível (Linux/macOS/WSL)

## Passo 1 — Instalar o plugin

```bash
/plugin add github.com/seu-user/argo
```

Ou manualmente, clone o repositório e adicione ao path do Claude Code.

## Passo 2 — Inicializar num projeto

Navegue até o projeto que você quer otimizar:

```bash
cd meu-projeto
/argo init
```

O ARGO vai criar:
```
meu-projeto/
├── harness/
│   └── CLAUDE.md         ← gerado automaticamente
├── benchmarks/
│   └── example_task/
│       ├── description.md
│       └── acceptance.sh
├── runs/                  ← vazio por enquanto
└── .argo/                 ← estado interno
```

## Passo 3 — Editar o harness inicial

Abra `harness/CLAUDE.md` e complete com as regras reais do seu projeto:
- Framework de testes usado
- Comando de build
- Convenções de código
- O que o agente nunca deve fazer

## Passo 4 — Ver traces existentes

Se você já usou o Claude Code neste projeto, veja os padrões de falha:

```bash
/argo logs
```

Saída esperada:
```
Padrão                    | Sessões | Turnos avg | Sugestão
--------------------------|---------|------------|---------------------------
Comandos repetidos        |       3 |       11.2 | Adicionar fallback no harness
```

## Passo 5 — Adicionar benchmarks reais

Para cada padrão de falha identificado, crie um benchmark:

```bash
/argo benchmark add
```

O wizard vai perguntar:
1. "Descreva a tarefa que o agente erra" → descreva em linguagem natural
2. "Como verificar que foi concluída?" → defina o critério

## Passo 6 — Primeiro run de otimização

```bash
/argo run --budget 3
```

O ARGO vai:
1. Ler seus traces e benchmarks
2. Propor 3 versões melhoradas do harness
3. Testar cada uma em sandbox
4. Promover a melhor automaticamente

## Passo 7 — Inspecionar os resultados

```bash
/argo inspect
```

Para ver o diff de um run específico:
```bash
/argo inspect 1
```

## Fluxo contínuo

A partir daí, o fluxo natural é:

1. Use Claude Code no projeto normalmente
2. Periodicamente: `/argo logs` para ver novos padrões
3. Adicione benchmarks para os padrões encontrados
4. Rode `/argo run` para otimizar
5. O harness melhora a cada ciclo
