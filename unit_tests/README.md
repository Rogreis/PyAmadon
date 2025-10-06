# unit_tests

Testes unitários rápidos e isolados para funcionalidades internas do projeto.

## Objetivos
- Garantir comportamento correto de componentes críticos sem precisar abrir a UI.
- Ajudar a refatorar com segurança (feedback rápido).
- Servir de exemplos executáveis de uso das classes/funções.

## Estrutura Atual
Arquivo | Cobertura
------- | ---------
`test_show_translation.py` | Extrai gzip simples, extrai tar.gz, verifica criação de pastas, valida status retornado por `verify_user_translations_choice`.

## Execução Básica
Com ambiente virtual ativo:
```bash
python -m pytest unit_tests -q
```

Executar testes verbosos:
```bash
python -m pytest unit_tests -vv
```

Parar na primeira falha:
```bash
python -m pytest unit_tests -q -x
```

Rodar somente um teste específico (por nome do arquivo):
```bash
python -m pytest unit_tests/test_show_translation.py::test_extract_archive_tar -vv
```

## Dependências de Teste
Instalar `pytest` (grupo dev):
```bash
uv add --group dev pytest
```
Após adicionar, o lock/instalação é atualizado automaticamente. Se necessário:
```bash
uv sync --group dev
```

## Cobertura de Código (opcional)
Adicionar ferramentas:
```bash
uv add --group dev coverage
```
Gerar relatório:
```bash
coverage run -m pytest unit_tests
coverage report -m
```

## Convenções de Escrita
- Prefixo de arquivo: `test_*.py`.
- Manter criação de dados artificiais em funções utilitárias dentro do próprio arquivo (evitar fixtures globais até que haja necessidade).
- Limpeza (teardown) simples: remover artefatos criados durante cada teste (feito em `teardown_function`).
- Evitar dependência de rede ou IO pesado.

## Boas Práticas
- Cada teste deve focar em uma única responsabilidade (arrange/act/assert).
- Mensagens de erro significativas: preferir asserts simples e diretos.
- Ao adicionar novos módulos no código fonte, criar ao menos um teste de caminho feliz (happy path) e um de erro.

## Integração com o uv
- Para atualizar dependências de teste: `uv lock --upgrade --group dev`.
- Para instalar sem dependências de desenvolvimento (ex: ambiente de produção): `uv sync --no-group dev`.

## Exclusão do Build
`unit_tests/` está em `excludes` dentro de `Amadon.spec` e, portanto, não é empacotado pelo PyInstaller. Não coloque código exclusivo de runtime aqui.

## Roadmap Sugerido
- Adicionar testes para módulos de toolbar (`tbar_functions/`).
- Validar internacionalização (`i18n.py`).
- Testar geração de ícones (se for mantido em script principal ou mover para tools/ com teste dedicado).

## Dúvidas Comuns
Pergunta | Resposta
-------- | -------
Por que não há `conftest.py`? | A complexidade atual é pequena; adicionamos quando surgirem fixtures reutilizáveis.
Por que não usar mocks? | Ainda não necessário; os testes manipulam somente sistema de arquivos temporário.
Cobertura mínima alvo? | Definir quando a base de testes crescer (ex: meta inicial 60%).

## Exemplos Rápidos
Validar apenas status de traduções (shell one‑liner):
```bash
python -c "from show_translations import ShowTranslation as ST; print(ST().verify_user_translations_choice([0,2,44]))"
```

---
Atualize este README quando novos conjuntos de testes forem adicionados.
