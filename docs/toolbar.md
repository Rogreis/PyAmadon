# Guia de Modificação da Toolbar

Este documento explica como a toolbar principal é construída, estilizada e como estender / alterar seu comportamento.

## Visão Geral
A toolbar fica centralizada no arquivo `main_window.py` dentro do método `_criar_menus_e_toolbar`. Ela:
- Cria ações principais (Documentos, Assuntos, Artigos, Busca, Configuração, Ajuda)
- Define ícones via `QIcon.fromTheme` (com fallback usando `QStyle`)
- Aplica estilo custom (gradiente azul + hover dourado) em `_apply_toolbar_style`
- Usa um `QActionGroup` exclusivo para manter um item marcado (estado persistente visual)
- Expõe um botão de alternância de tema (texto alterna entre Dark / Light)

## Estrutura de Código Principal
Local: `main_window.py`

Funções relevantes:
- `_criar_menus_e_toolbar()`: cria e configura tudo
- `_apply_toolbar_style()`: injeta o stylesheet da toolbar
- `_update_dark_toggle_action()`: atualiza texto/tooltip do botão de tema
- Handlers `_abrir_<modulo>()`: marcam ação correspondente como checked

Trechos importantes (simplificado):
```python
toolbar = QToolBar("Principal")
toolbar.setObjectName("MainToolBar")
toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
self._action_documentos = QAction(self._theme_icon(...), "&Documentos", self)
# ... (outras ações)
toolbar.addAction(self._action_documentos)
...
self._toolbar_action_group = QActionGroup(self)
self._action_documentos.setCheckable(True)
self._toolbar_action_group.addAction(self._action_documentos)
...
self._apply_toolbar_style()
self._update_dark_toggle_action()
```

## Estilo (QSS)
Definido em `_apply_toolbar_style()`:
- Seletores: `QToolBar#MainToolBar`, `QToolButton`, estados `:hover`, `:checked`, `:disabled`.
- Se quiser um tema alternativo, crie uma versão adicional (ex.: `_apply_toolbar_style_dark`) e chame-a conforme `settings.dark_mode`.
- Para adicionar efeitos extras (ex.: foco via teclado), adicione seletor `QToolBar#MainToolBar QToolButton:focus`.

## Adicionando uma Nova Ação
1. Criar a ação:
	```python
	self._action_novo = QAction(self._theme_icon("some-icon", QStyle.StandardPixmap.SP_FileIcon), "&Novo", self)
	self._action_novo.setToolTip("Descrição")
	self._action_novo.triggered.connect(self._abrir_novo)
	```
2. Adicionar ao toolbar na posição desejada.
3. Adicionar ao grupo se quiser comportamento de seleção exclusiva:
	```python
	self._action_novo.setCheckable(True)
	self._toolbar_action_group.addAction(self._action_novo)
	```
4. Criar método `_abrir_novo(self)` que instancia uma classe `ToolBar_<Nome>` (seguindo padrão existente) ou injeta diretamente conteúdo.

## Ícones
- Usa `_theme_icon(nome, fallback)` que tenta `QIcon.fromTheme` e cai para `style().standardIcon(fallback)`.
- Para ícones custom, adicione um diretório `assets/icons` e carregue com `QIcon(str(path))`.
- Se quiser ícones diferentes para dark mode, implemente lógica dentro `_theme_icon` verificando `settings.dark_mode`.

## Sincronizando Estado Visual
- Cada método `_abrir_<modulo>` chama `self._action_<modulo>.setChecked(True)`.
- Se criar módulo novo, lembre de repetir essa linha para garantir persistência visual.
- Para sincronizar via atalho de teclado, basta acionar `QAction.trigger()`.

## Alternância Dark / Light
Botão criado como `_action_toggle_dark`:
```python
self._action_toggle_dark = QAction("Dark", self)
```
- Atalho: `Ctrl+Alt+D`
- Ao alternar: muda `settings.dark_mode`, reaplica `apply_global_theme(app)`, atualiza documentos via `_update_embedded_docs_theme()`, e chama `_update_dark_toggle_action()`.
- Para alterar ícone conforme tema, inserir no final do toggle:
  ```python
  self._action_toggle_dark.setIcon(QIcon("assets/icons/moon.svg" if is_dark else "assets/icons/sun.svg"))
  ```

## Melhores Práticas
- Manter nomes consistentes: `_action_<nome>` para fácil busca.
- Evitar lógica de negócio dentro dos handlers de toolbar; delegar para classes `ToolBar_*`.
- Centralizar estilos em métodos dedicados para facilitar criação de tema alternativo.
- Usar `QActionGroup` para evitar ter que desmarcar manualmente ações anteriores.

## Extensões Futuras Sugeridas
| Ideia | Descrição | Complexidade |
|-------|-----------|--------------|
| Sub-toolbar contextual | Mostrar ações extras conforme módulo ativo | Média |
| Overflow / Menu lateral | Mover ações menos usadas para menu drop | Média |
| Layout vertical opcional | Toolbar lateral esquerda | Média/Alta |
| Persistir ordem do usuário | Permitir rearrastar ações | Alta |
| Animação hover | Efeito de scale leve no ícone | Baixa |

## Pontos de Atenção
- Estilos globais (QSS) podem sobrescrever estilos da toolbar se usarem seletores genéricos.
- Evitar `.setStyleSheet` por ação individual (fragmenta declaração). Centralizar no método.
- Ao adicionar grande quantidade de ações, considerar ícones menores (`setIconSize(QSize(24,24))`).

## Depuração Rápida
1. Ação não responde? Verificar se `triggered.connect` foi feito.
2. Ícone não aparece? Testar `icon.isNull()` após criação.
3. Tema não aplica? Confirmar chamada a `_apply_toolbar_style()` pós-modificação.
4. Botão de tema não muda texto? Ver `_update_dark_toggle_action` (foi chamado?).

## Checklist ao Modificar
- [ ] Ação adicionada ao toolbar
- [ ] Ação adicionada ao `QActionGroup` (se preciso)
- [ ] Handler implementado
- [ ] Estado `checked` atualizado ao abrir módulo
- [ ] Tooltip informativa
- [ ] Ícone válido (tema ou fallback)
- [ ] Estilo ajustado se necessário

---
Precisa de exemplo prático de extensão? Solicite e podemos gerar um protótipo de nova ação estruturada.
