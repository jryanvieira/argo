# Skill: sandbox

Você sabe como testar propostas de harness em isolamento seguro.

## Protocolo obrigatório

Antes de promover qualquer proposta de harness:

1. Verifique que a proposta só contém arquivos dentro de `harness/`
   - Se houver arquivos fora → status = `scope-violation`, não prossiga
2. Copie `proposed_harness/` para um diretório temporário isolado
3. Execute cada `acceptance.sh` em `benchmarks/*/` dentro desse diretório
4. Registre para cada benchmark: passou/falhou, tempo de execução, output
5. **NUNCA modifique o workspace original antes de aprovação**
6. Se qualquer benchmark crashar ou dar timeout → status = `crash`, não promova

## Critério de promoção

| Condição | Status | Ação |
|----------|--------|------|
| Score > melhor atual | `keep` | Promover e substituir harness/ |
| Score ≤ melhor atual | `discard` | Descartar |
| Qualquer crash/timeout | `crash` | Não promover |
| Arquivo fora de harness/ | `scope-violation` | Descartar imediatamente |
| Proposta vazia | `no-change` | Registrar e continuar |

## Isolamento

O sandbox garante que:
- Erros nos benchmarks não afetam o projeto
- Cada proposta é testada em estado limpo
- O histórico de runs fica intacto mesmo com crashes
