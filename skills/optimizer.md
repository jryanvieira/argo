# Skill: optimizer

Você sabe como orquestrar o loop completo de otimização do ARGO.

## Visão geral do loop

```
Para cada iteração (até budget):
  1. Ler histórico de runs anteriores
  2. Extrair traces de falha das sessões recentes
  3. Escrever context.md com harness atual + traces + histórico
  4. [PAUSA] Claude Code lê context.md → propõe harness melhorado
  5. Verificar escopo da proposta
  6. Testar em sandbox isolado
  7. Salvar artefatos no filesystem
  8. Promover se score melhorou
```

## Como executar

```bash
# Via CLI diretamente
python core/optimizer.py --project /caminho/projeto --budget 3

# Com aprovação humana
python core/optimizer.py --budget 3 --require-approval

# Sem modo interativo (proposta já presente)
python core/optimizer.py --budget 1 --no-interactive
```

## Papel do Claude Code no loop

O Python prepara o contexto e aguarda. O Claude Code:
1. Lê `.argo/context.md`
2. Usa a skill `proposer` para gerar `.argo/proposed_harness/`
3. Sinaliza: `touch .argo/proposal_ready`

O Python detecta o sinal e retoma o loop.

## Invariantes

- O Python nunca chama a API diretamente
- O workspace só é modificado na etapa de promoção, após testes
- Cada run é armazenado permanentemente, mesmo se descartado
- O score máximo histórico é preservado entre sessões
