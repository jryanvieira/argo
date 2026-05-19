# Skill: tracer

Você sabe interpretar traces de sessões do Claude Code para identificar sinais de harness fraco.

## Sinais de harness fraco

| Sinal | Descrição | Impacto |
|-------|-----------|---------|
| **Sessão longa** | Mais de 8 turnos para tarefa simples | Harness não clarifica o objetivo |
| **Comando repetido** | Mesmo comando bash executado 3+ vezes seguidas | Agente não sabe o que fazer após falha |
| **Correção manual** | Usuário enviou mensagem curta corrigindo o agente | Informação faltando no CLAUDE.md |
| **Pergunta óbvia** | Agente perguntou algo que deveria saber pelo CLAUDE.md | Harness incompleto |

## Como extrair traces

1. Leia os JSONLs em `~/.claude/projects/**/*.jsonl`
2. Filtre pelas últimas N sessões ou pelos últimos N dias
3. Para cada sessão:
   - Conte os turnos (mensagens user + assistant)
   - Extraia os tool_use de tipo `Bash` e verifique repetições
   - Verifique mensagens curtas do usuário após erros do agente
4. Para cada falha identificada:
   - O que o agente tentou
   - Onde errou
   - Como foi corrigido

## Formato de saída

```
Trace: {project}/{session_id}
- Timestamp: ...
- Turnos: N
- Sinais: sessão longa, comandos repetidos
- Comandos repetidos: ["git status", ...]
- Correções manuais: ["usa pytest", ...]
```

## Interpretação

- **Sessão longa + sem correções** → objetivo ambíguo no harness
- **Comandos repetidos** → falta instrução de fallback no harness
- **Muitas correções** → informações críticas faltando no CLAUDE.md
- **Combinação de sinais** → harness precisa de revisão completa
