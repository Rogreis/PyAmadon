# Pasta `tools/`

Scripts auxiliares de desenvolvimento. Não fazem parte do produto final.

## Como garantir que não entram no build (PyInstaller)
- Não importar estes scripts em `main.py` ou em módulos alcançados por ele.
- A especificação `Amadon.spec` lista apenas `main.py` como entrypoint.
- Se algum dia precisar importar utilidades sem arrastar tudo, mova só a função necessária para um módulo dentro do pacote principal.

## Exemplos
- `cleanup_cache.py`: limpa caches e logs.

## Boas práticas
- Não adicionar `__init__.py` aqui: mantém a pasta fora do namespace do pacote.
- Nomeie arquivos de forma explícita: `generate_*`, `check_*`, `dev_*`.
- Dependências extras? Use apenas stdlib ou coloque condicionalmente e documente.

## Rodando
```bash
python tools/cleanup_cache.py --dry-run
```

## Exclusão adicional (opcional)
Se quiser forçar exclusão na build mesmo que haja um import acidental, adicione `excludes=['tools']` em `Analysis()` ou ajuste `datas`.
