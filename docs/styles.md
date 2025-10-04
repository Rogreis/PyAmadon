# Guia de Estilos, Temas e Transições

Este documento descreve como os temas (dark/light), estilos globais, estilos de documentos e transições são aplicados no projeto.

## Componentes de Estilo
1. Stylesheet global (aplicado ao `QApplication`): `app_settings.py` (`global_stylesheet`)  
2. Estilo da toolbar: `_apply_toolbar_style()` em `main_window.py`  
3. Conteúdo de documentos (HTML/Markdown): gerado em `inject_web_content` / `inject_markdown` (`tbar_0base.py`)  
4. Transição e placeholder de carregamento: também em `inject_web_content`.  

## 1. Stylesheet Global
Arquivo: `app_settings.py` (função `settings.global_stylesheet()`).

Define regras para:
- Background base (`QWidget`) e paleta de texto
- Barras: `QStatusBar` e `QSplitter::handle`
- Campos: `QLineEdit`, `QTreeWidget`, `QTextEdit`
- Botões (`QPushButton`)
- Labels identificadas por `objectName` (status curto/longo/principal)
- Painéis: `QWidget#LeftPanel`, `QWidget#RightPanel`
- Itens de árvore: `QTreeView::item`, estados `:selected` e `:hover`

Para alterar um estilo global, modifique a string retornada. Exemplo para mudar cor base do tema claro:
```python
QWidget { background-color:#fafbfc; color:#202124; }
```
Reaplicar via `apply_global_theme(app)`.

### Extensão Possível
Separar os estilos em arquivos `.qss` externos e carregá-los dinamicamente para facilitar manutenção.

## 2. Toolbar
Estilos encapsulados em `_apply_toolbar_style()`. Não dependem do tema global para manter identidade visual. Se quiser sincronizar com dark mode, adicione verificação em `settings.dark_mode` e construa duas variantes.

## 3. Estilo dos Documentos (WebEngine)
Gerado dinamicamente em `ToolBar_Base.inject_web_content`:
- Classes base: `doc-body`, `doc-theme-light`, `doc-theme-dark`
- Regras para: body, headings, parágrafos, links, `code`, `pre`, `table`, `blockquote`, scrollbars.
- Ajustes para markdown adicionados em `inject_markdown` usando seletores dependentes de `.doc-theme-*`.

Para adicionar novo componente (ex.: “nota” / callout):
```css
body.doc-body .note { border-left:4px solid #1565c0; padding:8px 12px; background:#f0f5fb; }
body.doc-theme-dark .note { background:#1e1e24; border-left-color:#90caf9; }
```
Inserir no bloco `theme_css` em `inject_web_content`.

## 4. Placeholder e Transição
No `inject_web_content`:
```html
<div id='__doc_loading_placeholder'> ... </div>
```
Regras:
```css
body.doc-body { opacity:0; transition: opacity .28s ease-in; }
body.doc-body.doc-loaded { opacity:1; }
```
JS adiciona `doc-loaded` no `DOMContentLoaded`, remove placeholder e gera fade-in suave.

### Alterar Duração
Modificar `.28s` em `transition: opacity .28s ease-in;`.

### Desativar Efeito (Ex. Acessibilidade)
Adicionar flag de configuração e condicionalmente omitir o CSS/JS de transição.

## 5. Atualização de Tema Dinâmica
Método: `MainWindow._update_embedded_docs_theme()`.
Executa JS para trocar classes do `<body>` sem recarregar página.
Se adicionar novas classes temáticas, assegure-se de incluí-las na remoção/adicionando no script.

## 6. Painéis Vazios
Painéis `LeftPanel` e `RightPanel` têm cor de fundo coerente com tema para evitar “flash” branco.
Caso precise exibir indicações temporárias (ex.: “Nenhum conteúdo”), injete um `QLabel` com estilo neutro.

## 7. Boas Práticas de Estilo
- Prefira classes com prefixo (`doc-*`) para evitar colisão com frameworks (Bootstrap).
- Evite inline style em HTML dos documentos finais; mantenha centralizado no gerador.
- Minimize número de `setStyleSheet` diretos em widgets isolados.
- Use variação mínima de cores principais para consistência (paleta primária, neutros, feedback).

## 8. Paleta Atual (Resumo)
| Papel | Light | Dark |
|-------|-------|------|
| Fundo app | #f5f7fa | #121212 |
| Fundo painel docs | #ffffff | #121212 |
| Fundo painel vazio | #f0f4f8 | #181a1c |
| Primário | #1565c0 | #1565c0 |
| Hover primário | #1e88e5 | #1e70cc (toolbar checked hover) |
| Código inline | #f0f2f5 | #1e1e1e |
| Bloco code | #f5f7fa | #272822 |
| Tabela borda | #c7d4e5 | #3a3f42 |
| Blockquote fundo | #f0f5fb | #1e1e24 |

## 9. Adicionando Tema Futuro (Ex.: Sépia)
1. Adicionar atributo (ex.: `theme_mode: str` em `AppSettings`).
2. Adaptar `global_stylesheet()` com bloco `elif self.theme_mode == 'sepia': ...`.
3. No WebEngine, inserir nova classe `doc-theme-sepia` e adicionar regra no script de troca.
4. Ajustar botão de alternância para ciclar entre temas.

## 10. Depuração de Estilos
| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| Flash branco | Tema aplicado depois da janela | Aplicar antes (feito) |
| Estilo de árvore não muda | Cache de QSS antigo / override local | Remover `setStyleSheet` direto (feito) |
| Conteúdo Web sem tema | Classes não aplicadas | Verificar `<body class='doc-body ...'>` |
| Fade não acontece | Classe `doc-loaded` não aplicada | Ver console DevTools (se habilitado) |

## 11. Checklist ao Alterar Estilos
- [ ] Mudança aplicada em local central (global / inject / toolbar)
- [ ] Tema dark continua legível (contraste WCAG básico)
- [ ] Tamanhos de fonte coerentes (evitar saltos grandes)
- [ ] Testado com alternância rápida Dark/Light
- [ ] Nenhum flash perceptível em transições

---
Precisa de um gerador de paleta ou script que valide contraste? Podemos adicionar futuramente.
