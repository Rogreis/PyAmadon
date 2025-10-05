# tools /

Scripts auxiliares de desenvolvimento. Não distribuídos no executável final.

## Motivo
Separar tarefas de manutenção (limpeza, geração, inspeção) do código da aplicação. Isso reduz risco de bloat e dependências acidentais no build.

## Como garantimos que não entram na build
1. Não há `__init__.py` aqui, logo não é pacote importável sem caminho explícito.
2. `Amadon.spec` contém `excludes=['tools']` na `Analysis`.
3. Evite imports de `tools.*` dentro de `main.py` ou módulos por ele importados.

## Convenções
- Nomes descritivos: `cleanup_cache.py`, `dev_check.py`, `gen_icons.py` (se não for parte do runtime).
- Use só stdlib sempre que possível.
- Scripts devem ter docstring inicial explicando propósito.

## Exemplos
- `cleanup_cache.py` limpa caches e logs.

## Execução
```bash
python tools/cleanup_cache.py --dry-run
```

## Próximos scripts sugeridos
- `verify_translations.py`: validar chaves em `resources/messages_*.json`.
- `dev_lint.py`: agregador para rodar linters/formatadores (se adicionados depois).

## Dependências somente de desenvolvimento (grupo `dev`)

O arquivo `pyproject.toml` já define um grupo:

```toml
[dependency-groups]
dev = [
	"pyinstaller>=6.16.0",
]
```

Use o `uv` para manipular dependências de desenvolvimento sem poluir o runtime de produção.

### Adicionar um pacote apenas ao grupo dev
Exemplo: adicionar `ruff` para lint.
```bash
uv add --group dev ruff
```
Isto altera `pyproject.toml` (e o `uv.lock`). Depois sincronize (se ainda não sincronizou):
```bash
uv sync --group dev
```
Observação: `uv sync` sem argumentos já instala todos os grupos definidos (por padrão), então normalmente basta:
```bash
uv sync
```

### Remover um pacote do grupo dev
```bash
uv remove --group dev ruff
uv sync
```

### Atualizar dependências do grupo dev
Todos:
```bash
uv lock --upgrade --group dev
uv sync
```
Somente um pacote:
```bash
uv lock --upgrade-package ruff
uv sync
```

### Listar dependências instaladas e distinguir grupos
```bash
uv pip list
```
Para ver o que está desatualizado:
```bash
uv pip list --outdated
```

### Instalar apenas runtime (sem dev)
Em um ambiente de produção você pode optar por não instalar o grupo `dev`:
```bash
uv sync --no-group dev
```

### Boas práticas
- Ferramentas de qualidade de código, empacotamento, geração ou scripts diagnósticos ficam em `dev`.
- Nunca coloque em `dev` algo necessário em tempo de execução da aplicação distribuída.
- Se um script dentro de `tools/` precisar de uma lib não-runtime, ela deve estar no grupo `dev`.

### Resumo rápido
| Ação | Comando |
|------|---------|
| Add dev | `uv add --group dev pacote` |
| Remove dev | `uv remove --group dev pacote` |
| Sync tudo | `uv sync` |
| Sync só runtime | `uv sync --no-group dev` |
| Upgrade dev | `uv lock --upgrade --group dev && uv sync` |
| Upgrade pacote | `uv lock --upgrade-package pacote && uv sync` |

Se tiver dúvidas sobre outro fluxo (ex: múltiplos grupos), pode pedir aqui.