---
description: Analisa traces de sessões recentes e lista padrões de harness fraco
---

# Comando: /argo logs

Analisa traces de sessões recentes e lista padrões de falha.

## Execução

1. Leia todos os JSONLs em `~/.claude/projects/**/*.jsonl` dos últimos 14 dias
2. Use a skill `tracer` para identificar padrões de falha
3. Agrupe por tipo de sinal e calcule frequência
4. Exiba tabela com top 5 padrões:

```
Padrão                          | Sessões | Turnos avg | Sugestão
--------------------------------|---------|------------|---------------------------
Comandos bash repetidos         |       8 |       12.3 | Adicionar instrução fallback
Correções manuais frequentes    |       5 |        9.1 | Completar informações no CLAUDE.md
Sessões longas sem conclusão    |       4 |       15.7 | Clarificar objetivo no harness
```

5. Pergunte: "Quer criar benchmarks baseados nesses padrões? [s/n]"
   - Se sim: execute `/argo benchmark add` para cada padrão identificado

## Interpretação automática

Para cada padrão, sugira automaticamente:

| Sinal | Sugestão de harness |
|-------|---------------------|
| Comando repetido "git status" | Adicionar: "após falha de git, verifique o estado com..." |
| Correção "usa pytest" | Adicionar: "framework de testes: pytest" |
| Sessão com 15+ turnos | Revisar se o objetivo da tarefa está claro |
