# {{project_name}}

## Contexto do projeto

{{project_description}}

**Linguagem principal:** {{language}}
**Estrutura:**
{{project_structure}}

## Ferramentas

{{tools_section}}

## Comandos essenciais

```bash
# Rodar testes
{{test_command}}

# Build
{{build_command}}

# Lint / formatação
{{lint_command}}
```

## Regras do agente

- Sempre rode os testes antes de considerar uma tarefa concluída
- Use {{test_framework}} para os testes
- Não modifique arquivos fora do escopo da tarefa solicitada
- Se um comando falhar, leia o output completo antes de tentar novamente
- {{extra_rules}}

## Estrutura de diretórios relevante

```
{{directory_tree}}
```

## Fluxo de trabalho padrão

1. Entenda o requisito antes de escrever código
2. Implemente a mudança mínima necessária
3. Rode os testes
4. Verifique se nada foi quebrado

## O que NÃO fazer

- Não instale dependências sem confirmar com o usuário
- Não faça commits automáticos sem instrução explícita
- Não rode comandos destrutivos (rm -rf, DROP TABLE) sem confirmação
