## Amadon

Aplicação desktop (PySide6) para leitura e estudo do Livro de Urântia.

### Funcionalidades atuais

- Barra de status com 3 áreas:
	- Campo curto (status rápido, 1 palavra)
	- Campo longo (descrição breve)
	- Área expansível com elipse automática e tooltip quando truncado
- Sistema de logging (arquivo + console) com opção de configuração avançada
- Ícone customizado dinâmico (livro aberto) + geração de ícones multi-resolução
- Ações de teste para demonstrar logs e status
- Build automatizado via PyInstaller e GitHub Actions (workflow de release por tag v*)

### Requisitos

- Python 3.12+
- uv (para sync rápido) ou pip

### Instalação (desenvolvimento)

```bash
uv sync --dev
# ou
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

### Rodar aplicação

```bash
uv run python main.py
# ou
python main.py
```

### Logging

Logs básicos: `amadon.log`

Se `logging_config.py` existir, a aplicação tenta usar logging avançado (rotação / separação de erros) via `AmalonLoggingConfig`.

### Barra de Status

Métodos disponíveis na `MainWindow`:

```python
self.atualizar_status_curto("Pronto")
self.atualizar_status_longo("Carregado")
self.set_status_mensagem("Mensagem principal que se expande e elide...")
self.set_status_temporario("Salvo!", 3000)  # restaura depois
```

### Ícones

Gerar ícones (PNG múltiplos e .ico):

```bash
python generate_icons.py
```

Saída em: `assets/icons/`

Usado no build do PyInstaller via `Amadon.spec` (campo `icon`).

### Build manual (local)

```bash
# Gera ícones (opcional se já existirem)
python generate_icons.py

# Build
pyinstaller Amadon.spec

# Resultado
dist/Amadon.exe  # Windows
```

### Release automatizado

1. Crie uma tag semântica: `git tag v0.1.0 && git push origin v0.1.0`
2. GitHub Actions compila (Windows + macOS) e anexa binários ao Release.

### Estrutura principal

```
main.py                # Janela principal e lógica UI
logging_config.py      # (Opcional) logging avançado
generate_icons.py      # Geração de ícones multi-size
assets/icons/          # Ícones gerados
Amadon.spec            # Configuração PyInstaller
.github/workflows/     # Pipeline de release
```

### Capturas de Tela

*(Adicione imagens em `assets/screenshots/` e referencie aqui, ex.:)*

```
![Janela Principal](assets/screenshots/main_window.png)
```

### Contribuindo

1. Faça um fork
2. Crie um branch: `git checkout -b feature/nome`
3. Commit: `git commit -m "Descrição clara"`
4. Push: `git push origin feature/nome`
5. Abra um Pull Request

Padrões sugeridos:
- Commits em português claro
- Código seguindo estilo PEP 8 (quando aplicável)
- Evitar dependências extras desnecessárias

### Próximas ideias (sugestões)

- Modo leitura com navegação por capítulos
- Pesquisa textual com indexação incremental
- Tema claro/escuro sincronizado ao SO
- Preferências do usuário persistidas (QSettings)
- Exportar trechos em Markdown / PDF

### Licença (MIT)

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

