# Conceitos fundamentais do ARGO

## O que é um harness?

Um **harness** é o conjunto de instruções que guia o comportamento de um coding agent numa sessão.
No Claude Code, o harness principal é o `CLAUDE.md` — o arquivo que define como o agente
deve se comportar, quais ferramentas usar, quais convenções seguir.

Um harness fraco causa sessões longas, erros repetidos e necessidade de intervenção manual.
Um harness forte reduz turnos desperdiçados e torna o agente mais autônomo.

## O que é o loop de otimização?

O loop do ARGO melhora o harness iterativamente:

```
sessão 1: você usa Claude Code normalmente
               ↓ traces salvos em ~/.claude/projects/
sessão 2: /argo run
               ↓ lê traces de falha
               ↓ Claude Code propõe novo harness
               ↓ testa em sandbox
               ↓ promove se melhorou
sessão 3: Claude Code começa com harness melhorado
```

Cada sessão é melhor que a anterior porque o harness acumula aprendizados reais.

## O que é um trace?

Um **trace** é o registro de uma sessão do Claude Code — armazenado como JSONL em
`~/.claude/projects/`. O ARGO lê esses traces para identificar onde o agente falhou.

**Sinais de harness fraco num trace:**
- Mais de 8 turnos para uma tarefa simples
- O mesmo comando bash executado 3+ vezes seguidas
- Mensagens curtas do usuário corrigindo o agente ("não, usa pytest")
- O agente perguntou algo que deveria saber pelo CLAUDE.md

## O que é um benchmark?

Um **benchmark** é uma tarefa concreta com critério de aceitação verificável.
Cada benchmark tem:
- `description.md` — o que o agente precisa fazer
- `acceptance.sh` — script bash que verifica se o harness cobre o requisito

O score de um run é a fração de benchmarks que passaram.

## O que é um run?

Um **run** é uma iteração do loop de otimização. Cada run:
1. Lê os traces recentes
2. Propõe um harness melhorado
3. Testa em sandbox
4. Salva o resultado em `runs/run_NNN/`

O harness só é promovido se o score melhorou em relação ao melhor run anterior.
