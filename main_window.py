"""Módulo contendo a classe principal da janela da aplicação Amadon.

Expõe uma variável global `main_window` que conterá a instância única de `MainWindow`
após a chamada da função `main()` deste módulo.
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QToolBar,
    QSizePolicy,
    QStyle,
    QSplitter,
    QWidget,
    QVBoxLayout,
    QFrame,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QActionGroup, QIcon, QPainter, QPen, QBrush, QColor, QLinearGradient, QPixmap

from mensagens import MensagensStatus, AmadonLogging
from i18n import _
from tbar_functions.tbar_documentos import ToolBar_Documentos
from tbar_functions.tbar_assuntos import ToolBar_Assuntos
from tbar_functions.tbar_artigos import ToolBar_Artigos
from tbar_functions.tbar_busca import ToolBar_Busca
from tbar_functions.tbar_configuracao import ToolBar_Configuracao
from tbar_functions.tbar_ajuda import ToolBar_Ajuda

# Importa configuração avançada de logging (opcional)
try:
    from logging_config import AmadonLoggingConfig
    USE_ADVANCED_LOGGING = True
except ImportError:  # pragma: no cover - fallback
    USE_ADVANCED_LOGGING = False


class ElidedLabel(QLabel):
    """QLabel que aplica elipse automática quando o texto não cabe."""
    def __init__(self, text: str = "", parent=None, elide_mode=Qt.TextElideMode.ElideRight):
        super().__init__(text, parent)
        self._full_text = text
        self._elide_mode = elide_mode
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def setText(self, text: str):  # type: ignore[override]
        self._full_text = text
        super().setText(text)
        self._update_elided()

    def resizeEvent(self, event):  # type: ignore[override]
        super().resizeEvent(event)
        self._update_elided()

    def _update_elided(self):
        metrics = self.fontMetrics()
        elided = metrics.elidedText(self._full_text, self._elide_mode, self.width() - 4)
        super().setText(elided)
        # Define tooltip apenas se houver truncamento
        if elided != self._full_text:
            self.setToolTip(self._full_text)
        else:
            self.setToolTip("")

    def fullText(self) -> str:
        return self._full_text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_logger()
        AmadonLogging.info(self, _("log.init.app"))
        self._apply_window_icon()
        self.setWindowTitle(_("app.title"))
        # Estado interno do modo de leitura (focus mode)
        self._focus_mode: bool = False
        # Restaura tamanho/posição se existir
        try:
            from app_settings import settings
            if settings.win_size:
                self.resize(*settings.win_size)
            else:
                self.resize(800, 600)
            if settings.win_pos:
                self.move(*settings.win_pos)
        except Exception:
            self.resize(800, 600)
        AmadonLogging.debug(self, _("log.window.ready"))
        # Área central agora é um splitter horizontal (30% / 70%)
        self._criar_area_central()

        # --- Barra de Status ---
        self.status_curto = QLabel(_("status.pronto"))
        self.status_curto.setObjectName("StatusCurtoLabel")
        self.status_curto.setFixedWidth(80)
        self.status_longo = QLabel(_("status.sistema_inicializado"))
        self.status_longo.setObjectName("StatusLongoLabel")
        self.status_longo.setFixedWidth(200)

        self.statusBar().addWidget(self.status_curto)
        self.statusBar().addWidget(self.status_longo)

        self.status_msg = ElidedLabel(_("app.title"), elide_mode=Qt.TextElideMode.ElideRight)
        self.status_msg.setObjectName("StatusPrincipalLabel")
        self.statusBar().addPermanentWidget(self.status_msg, 1)

        # Constrói menus e toolbar específicos da aplicação
        self._criar_menus_e_toolbar()
        # Reabre último módulo ou abre Documentos se não definido
        try:
            from app_settings import settings as _settings
            mapping = {
                'documentos': self._abrir_documentos,
                'assuntos': self._abrir_assuntos,
                'artigos': self._abrir_artigos,
                'busca': self._abrir_busca,
                'configuracao': self._abrir_configuracao,
                'ajuda': self._abrir_ajuda,
            }
            # Se o último módulo era 'configuracao', forçamos a abrir 'documentos'
            if _settings.last_module == 'configuracao':
                _settings.last_module = 'documentos'
                try:
                    _settings.save()
                except Exception:
                    pass
                self._abrir_documentos()
            else:
                (mapping.get(_settings.last_module) or self._abrir_documentos)()
        except Exception:
            self._abrir_documentos()

    # --- Logging ---
    def _setup_logger(self):
        if USE_ADVANCED_LOGGING:
            self.logger = AmadonLoggingConfig.setup_advanced_logging('Amadon')
            AmadonLogging.info(self, _("log.init.app"))
        else:
            self._setup_basic_logger()

    def _setup_basic_logger(self):
        self.logger = logging.getLogger('Amadon')
        self.logger.setLevel(logging.DEBUG)
        if self.logger.handlers:
            self.logger.handlers.clear()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = logging.FileHandler('amadon.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.propagate = False

    # --- Status Helpers ---
    def set_status_temporario(self, texto: str, ms: int = 3000):
        MensagensStatus.temporario_principal(self, texto, ms)

    def clear_status_mensagem(self):
        MensagensStatus.limpar_principal(self)
        AmadonLogging.debug(self, _("log.status.cleared"))

    def atualizar_status_curto(self, texto: str):
        MensagensStatus.curto(self, texto)

    def atualizar_status_longo(self, texto: str):
        MensagensStatus.longo(self, texto)

    def set_status_mensagem(self, texto: str):
        MensagensStatus.principal(self, texto)

    def atualizar_ambos_status(self, curto: str, longo: str):
        MensagensStatus.ambos(self, curto, longo)

    # --- Área central (splitter) ---
    def _criar_area_central(self):
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        # Painel esquerdo (30%) - sem placeholder inicial
        left = QWidget(splitter)
        left.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(6, 6, 6, 6)
        left_layout.setSpacing(4)

        # Painel direito (70%) - sem placeholder inicial
        right = QWidget(splitter)
        right.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(6, 6, 6, 6)
        right_layout.setSpacing(4)

        splitter.addWidget(left)
        splitter.addWidget(right)

        # Guarda referências se necessário futuramente
        self.splitter = splitter
        self.left_panel = left
        self.right_panel = right

        # Estilo do handle para ficar mais visível
        from app_settings import settings as _settings_theme
        if _settings_theme.dark_mode:
            splitter.setStyleSheet(
                """
                QSplitter::handle { background-color:#2a2a2a; border:1px solid #3a3a3a; margin:0; }
                QSplitter::handle:hover { background-color:#3a3a3a; }
                QSplitter::handle:pressed { background-color:#1565c0; }
                """
            )
        else:
            splitter.setStyleSheet(
                """
                QSplitter::handle { background-color:#0a3d7a; border:1px solid #082b52; margin:0; }
                QSplitter::handle:hover { background-color:#1565c0; }
                QSplitter::handle:pressed { background-color:#0d47a1; }
                """
            )

        self.setCentralWidget(splitter)

        # Ajusta proporções iniciais após o layout estar pronto
        from PySide6.QtCore import QTimer
        from app_settings import settings as _settings2
        def _apply_sizes():
            if _settings2.splitter_sizes:
                splitter.setSizes(_settings2.splitter_sizes)
            else:
                splitter.setSizes(self._calc_split_sizes())
        QTimer.singleShot(0, _apply_sizes)

    def _calc_split_sizes(self):
        total = max(self.width(), 1)
        left = int(total * 0.30)
        right = total - left
        return [left, right]

    # --- Ações ---
    # --- Novas ações principais ---
    def _criar_menus_e_toolbar(self):
        """Cria menu bar e toolbar com ações principais da aplicação."""
        menu_bar = self.menuBar()

        # Limpa menus existentes (se reconstruir futuramente)
        while menu_bar.actions():
            menu_bar.removeAction(menu_bar.actions()[0])

        # Ações: cada uma com ícone (tentando tema; fallback simples se ausente)
        # Usa ícones de tema quando disponíveis; caso contrário, fallback para ícones padrão do QStyle
        self._action_documentos = QAction(self._theme_icon("folder-documents", QStyle.StandardPixmap.SP_DirIcon), f"&{_("toolbar.documentos")}", self)
        self._action_assuntos = QAction(self._theme_icon("view-list", QStyle.StandardPixmap.SP_FileDialogListView), f"&{_("toolbar.assuntos")}", self)
        self._action_artigos = QAction(self._theme_icon("text-x-generic", QStyle.StandardPixmap.SP_FileIcon), f"&{_("toolbar.artigos")}", self)
        self._action_busca = QAction(self._theme_icon("edit-find", QStyle.StandardPixmap.SP_DialogOpenButton), f"&{_("toolbar.busca")}", self)
        self._action_config = QAction(self._theme_icon("settings", QStyle.StandardPixmap.SP_FileDialogDetailedView), f"&{_("toolbar.configuracao")}", self)
        self._action_ajuda = QAction(self._theme_icon("help-browser", QStyle.StandardPixmap.SP_DialogHelpButton), f"&{_("toolbar.ajuda")}", self)

        # Tooltips detalhados
        self._action_documentos.setToolTip(_("tooltip.documentos"))
        self._action_assuntos.setToolTip(_("tooltip.assuntos"))
        self._action_artigos.setToolTip(_("tooltip.artigos"))
        self._action_busca.setToolTip(_("tooltip.busca"))
        self._action_config.setToolTip(_("tooltip.configuracao"))
        self._action_ajuda.setToolTip(_("tooltip.ajuda"))

        # Conecta sinais às rotinas privadas
        self._action_documentos.triggered.connect(self._abrir_documentos)
        self._action_assuntos.triggered.connect(self._abrir_assuntos)
        self._action_artigos.triggered.connect(self._abrir_artigos)
        self._action_busca.triggered.connect(self._abrir_busca)
        self._action_config.triggered.connect(self._abrir_configuracao)
        self._action_ajuda.triggered.connect(self._abrir_ajuda)

        # # Menus (podemos agrupar conforme evolução futura)
        # menu_conteudo = menu_bar.addMenu("&Conteúdo")
        # menu_conteudo.addAction(self._action_documentos)
        # menu_conteudo.addAction(self._action_assuntos)
        # menu_conteudo.addAction(self._action_artigos)
        # menu_conteudo.addSeparator()
        # menu_conteudo.addAction(self._action_busca)

        # menu_sistema = menu_bar.addMenu("&Sistema")
        # menu_sistema.addAction(self._action_config)
        # menu_sistema.addAction(self._action_ajuda)

        # Toolbar principal
        toolbar = QToolBar("Principal")
        toolbar.setObjectName("MainToolBar")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        self._main_toolbar = toolbar
        # Ação atalho modo escuro
        from PySide6.QtGui import QKeySequence
        from app_settings import settings as _settings, apply_global_theme
        self._action_toggle_dark = QAction("Dark", self)
        self._action_toggle_dark.setShortcut(QKeySequence("Ctrl+Alt+D"))
        self._action_toggle_dark.setToolTip("Alternar modo escuro (Ctrl+Alt+D)")
        def _toggle_dark():
            _settings.dark_mode = not _settings.dark_mode
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                apply_global_theme(app)
                # Atualiza tema dos documentos embutidos sem reinjetar
                try:
                    self._update_embedded_docs_theme()
                except Exception:
                    pass
            _settings.save()
        self._action_toggle_dark.triggered.connect(_toggle_dark)
        # Ações na ordem desejada
        toolbar.addAction(self._action_documentos)
        toolbar.addAction(self._action_assuntos)
        toolbar.addAction(self._action_artigos)
        toolbar.addSeparator()
        toolbar.addAction(self._action_busca)
        toolbar.addSeparator()
        toolbar.addAction(self._action_config)
        toolbar.addAction(self._action_ajuda)
        toolbar.addSeparator()
        toolbar.addAction(self._action_toggle_dark)
        # Ação modo leitura (focus) - F11
        self._action_focus = QAction(_("action.focus.enter"), self)
        # Atalho F11 será tratado por QShortcut e keyPressEvent; não definimos no QAction para evitar ambiguidade
        self._action_focus.setToolTip(_("tooltip.focus.enter"))
        self._action_focus.triggered.connect(self._toggle_focus_mode)
        toolbar.addAction(self._action_focus)

        # Torna ações principais 'checkable' para manter highlight após clique
        self._toolbar_action_group = QActionGroup(self)
        self._toolbar_action_group.setExclusive(True)
        primary_actions = [
            self._action_documentos,
            self._action_assuntos,
            self._action_artigos,
            self._action_busca,
            self._action_config,
            self._action_ajuda,
        ]
        for act in primary_actions:
            act.setCheckable(True)
            self._toolbar_action_group.addAction(act)
        self._primary_toolbar_actions = primary_actions

        self._apply_toolbar_style()
        # Ajusta rótulo inicial do toggle Dark/Light
        self._update_dark_toggle_action()
        # Ajusta rótulo inicial do modo leitura
        self._update_focus_action()
        # Atalhos dedicados (garantem funcionamento mesmo com toolbar oculta)
        from PySide6.QtGui import QShortcut, QKeySequence
        # Apenas um QShortcut (F11); se houver ambiguidade futura, podemos migrar para um atalho alternativo configurável
        self._shortcut_focus_toggle = QShortcut(QKeySequence("F11"), self)
        self._shortcut_focus_toggle.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self._shortcut_focus_toggle.activated.connect(self._toggle_focus_mode)
        # ESC sai do modo leitura se ativo
        self._shortcut_focus_escape = QShortcut(QKeySequence("Esc"), self)
        self._shortcut_focus_escape.setContext(Qt.ShortcutContext.ApplicationShortcut)
        def _esc_exit():
            if getattr(self, '_focus_mode', False):
                self._toggle_focus_mode()
        self._shortcut_focus_escape.activated.connect(_esc_exit)

    def _apply_toolbar_style(self):
        """Aplica estilo azul clássico à toolbar com hover dourado e item selecionado persistente."""
        # Estilo independente do tema global (pode evoluir futuramente para variantes dark/light)
        stylesheet = """
        QToolBar#MainToolBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #0d47a1, stop:1 #0a3d8f);
            border: 0px;
            padding: 4px;
            spacing: 4px;
        }
        QToolBar#MainToolBar QToolButton {
            background: transparent;
            color: white;
            border-radius: 6px;
            padding: 4px 6px 2px 6px;
            margin: 2px;
        }
        QToolBar#MainToolBar QToolButton:hover {
            background: #1565c0;
            color: gold;
        }
        QToolBar#MainToolBar QToolButton:pressed {
            background: #0b437f;
        }
        QToolBar#MainToolBar QToolButton:checked {
            background: #1565c0;
            color: gold;
            border: 1px solid #e0c060;
        }
        QToolBar#MainToolBar QToolButton:checked:hover {
            background: #1e70cc;
        }
        QToolBar#MainToolBar QToolButton:disabled {
            color: #cccccc;
            background: #0d47a1;
        }
        """
        if hasattr(self, '_main_toolbar'):
            self._main_toolbar.setStyleSheet(stylesheet)

    def _update_dark_toggle_action(self):
        """Atualiza texto e tooltip do botão de alternância de tema (Dark/Light)."""
        if not hasattr(self, '_action_toggle_dark'):
            return
        try:
            from app_settings import settings as _settings
            is_dark = bool(getattr(_settings, 'dark_mode', False))
        except Exception:
            is_dark = False
        if is_dark:
            self._action_toggle_dark.setText("Light")
            self._action_toggle_dark.setToolTip("Alternar para modo claro (Ctrl+Alt+D)")
        else:
            self._action_toggle_dark.setText("Dark")
            self._action_toggle_dark.setToolTip("Alternar para modo escuro (Ctrl+Alt+D)")

    # --- Focus / Reading Mode ---
    def _toggle_focus_mode(self):
        """Alterna o modo de leitura.

        Entrada no modo leitura:
          - Oculta menubar, toolbar principal e barra de status
          - Oculta painel esquerdo (navegação) e expande conteúdo
          - Salva tamanhos originais do splitter e geometria da janela
          - Vai para tela cheia (fullscreen) para leitura sem distrações
          - Injeta classe CSS em WebViews para melhorar legibilidade

        Saída restaura tudo.
        """
        entering = not self._focus_mode
        if entering:
            # Salva estado anterior apenas na entrada
            try:
                self._focus_prev_state = {
                    'split_sizes': getattr(self.splitter, 'sizes', lambda: [])(),
                    'geometry': self.saveGeometry(),
                    'win_w': self.width(),
                    'win_h': self.height(),
                    'was_fullscreen': self.isFullScreen(),
                    'was_maximized': self.isMaximized(),
                    'left_visible': getattr(self.left_panel, 'isVisible', lambda: True)(),
                    'status_visible': self.statusBar().isVisible()
                }
            except Exception:
                self._focus_prev_state = {}
        self._focus_mode = entering
        # Menubar & toolbar
        try:
            mb = self.menuBar()
            if mb:
                mb.setVisible(not self._focus_mode)
        except Exception:
            pass
        try:
            if hasattr(self, '_main_toolbar'):
                self._main_toolbar.setVisible(not self._focus_mode)
        except Exception:
            pass
        # Status bar
        try:
            self.statusBar().setVisible(not self._focus_mode)
        except Exception:
            pass
        # Painel esquerdo / splitter
        try:
            if self._focus_mode:
                if hasattr(self, 'left_panel'):
                    self.left_panel.setVisible(False)
                if hasattr(self, 'splitter'):
                    self.splitter.setSizes([0, max(1, self.width())])
            else:
                if hasattr(self, 'left_panel') and self._focus_prev_state.get('left_visible', True):
                    self.left_panel.setVisible(True)
                if hasattr(self, 'splitter'):
                    prev = self._focus_prev_state.get('split_sizes') if hasattr(self, '_focus_prev_state') else None
                    if prev and isinstance(prev, list) and len(prev) == 2:
                        self.splitter.setSizes(prev)
        except Exception:
            pass
        # Fullscreen / restore
        try:
            if self._focus_mode:
                self.showFullScreen()
            else:
                # Sai do fullscreen primeiro
                if self.isFullScreen():
                    self.showNormal()
                # Restaura estado anterior
                prev = getattr(self, '_focus_prev_state', {})
                if prev.get('was_maximized') and not prev.get('was_fullscreen'):
                    self.showMaximized()
        except Exception:
            pass
        # Ajusta CSS nos WebViews
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
            js_prepare = """(function(){if(!document.getElementById('focusReadingStyle')){var s=document.createElement('style');s.id='focusReadingStyle';s.textContent='body.focus-reading{max-width:1100px;margin:0 auto;padding:28px 40px;font-size:1.08em;line-height:1.5;}';document.head.appendChild(s);}})();"""
            js_add = "(function(){document.body&&document.body.classList.add('focus-reading');})();"
            js_remove = "(function(){document.body&&document.body.classList.remove('focus-reading');})();"
            for panel_name in ('left_panel', 'right_panel'):
                panel = getattr(self, panel_name, None)
                if not panel:
                    continue
                for view in panel.findChildren(QWebEngineView):
                    try:
                        if self._focus_mode:
                            view.page().runJavaScript(js_prepare)
                            view.page().runJavaScript(js_add)
                        else:
                            view.page().runJavaScript(js_remove)
                    except Exception:
                        pass
        except Exception:
            pass
        # Atualiza ação
        self._update_focus_action()
        # Mensagem de status
        if self._focus_mode:
            self.set_status_temporario(_("status.focus.on"), 3000)
        else:
            self.set_status_temporario(_("status.focus.off"), 3000)

    def _update_focus_action(self):
        if not hasattr(self, '_action_focus'):
            return
        if self._focus_mode:
            self._action_focus.setText(_("action.focus.exit"))
            self._action_focus.setToolTip(_("tooltip.focus.exit"))
        else:
            self._action_focus.setText(_("action.focus.enter"))
            self._action_focus.setToolTip(_("tooltip.focus.enter"))

    def _update_embedded_docs_theme(self):
        """Atualiza dinamicamente o tema (dark/light) dos QWebEngineView já carregados.

        Troca somente a classe do <body> sem reinjetar todo o conteúdo para preservar
        posição de scroll e estado JS leve.
        """
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
        except Exception:  # pragma: no cover
            return
        try:
            from app_settings import settings as _settings
            is_dark = bool(getattr(_settings, 'dark_mode', False))
        except Exception:  # pragma: no cover
            is_dark = False
        target_class = 'doc-theme-dark' if is_dark else 'doc-theme-light'
        js = f"(function(cls){{const b=document.body;if(!b)return;b.classList.remove('doc-theme-light','doc-theme-dark');b.classList.add(cls);}})('{target_class}');"
        for panel_name in ('left_panel', 'right_panel'):
            panel = getattr(self, panel_name, None)
            if not panel:
                continue
            # Remove estilos inline específicos antigos (caso algum tivesse sido aplicado)
            # deixamos apenas estilos mínimos configurados na criação (opcional futura limpeza)
            for view in panel.findChildren(QWebEngineView):
                try:
                    view.page().runJavaScript(js)
                except Exception:
                    pass

    def _theme_icon(self, theme_name: str, fallback_sp: QStyle.StandardPixmap) -> QIcon:
        """Tenta obter um ícone pelo nome de tema; se não existir (comum no Windows), usa fallback do QStyle.

        Parameters
        ----------
        theme_name : str
            Nome do ícone no tema (ex.: 'folder-documents').
        fallback_sp : QStyle.StandardPixmap
            Enum de ícone padrão para fallback.
        """
        icon = QIcon.fromTheme(theme_name)
        if icon.isNull():
            icon = self.style().standardIcon(fallback_sp)
        return icon

    # Handlers privados (placeholders)
    def _abrir_documentos(self):
        from app_settings import settings
        settings.last_module = 'documentos'
        tb = ToolBar_Documentos(self)
        html = tb.GenerateData()
        if html:
            tb.inject_web_content(html, target='right', clear=True, use_bootstrap=True, css=tb.css_right(), js=tb.js_right())
        tb.Show()
        if hasattr(self, '_action_documentos'):
            self._action_documentos.setChecked(True)

    def _abrir_assuntos(self):
        from app_settings import settings
        settings.last_module = 'assuntos'
        tb = ToolBar_Assuntos(self)
        html = tb.GenerateData()
        if html:
            tb.inject_web_content(html, target='left', clear=True, use_bootstrap=False, css=tb.css_left())
        tb.Show()
        if hasattr(self, '_action_assuntos'):
            self._action_assuntos.setChecked(True)

    def _abrir_artigos(self):
        from app_settings import settings
        settings.last_module = 'artigos'
        tb = ToolBar_Artigos(self)
        html = tb.GenerateData()
        if html:
            tb.inject_web_content(html, target='left', clear=True, css=tb.css_left())
        tb.Show()
        if hasattr(self, '_action_artigos'):
            self._action_artigos.setChecked(True)

    def _abrir_busca(self):
        from app_settings import settings
        settings.last_module = 'busca'
        tb = ToolBar_Busca(self)
        html = tb.GenerateData()
        if html:
            tb.inject_web_content(html, target='left', clear=True, css=tb.css_left())
        tb.Show()
        if hasattr(self, '_action_busca'):
            self._action_busca.setChecked(True)

    def _abrir_configuracao(self):
        from app_settings import settings
        settings.last_module = 'configuracao'
        tb = ToolBar_Configuracao(self)
        html = tb.GenerateData()
        if html:
            tb.inject_web_content(html, target='left', clear=True, css=tb.css_left())
        tb.Show()
        if hasattr(self, '_action_config'):
            self._action_config.setChecked(True)

    def _abrir_ajuda(self):
        from app_settings import settings
        settings.last_module = 'ajuda'
        tb = ToolBar_Ajuda(self)
        html = tb.GenerateData()
        if html:
            tb.inject_web_content(html, target='left', clear=True, use_bootstrap=True, css=tb.css_left(), js=tb.js_left())
        tb.Show()
        if hasattr(self, '_action_ajuda'):
            self._action_ajuda.setChecked(True)

    def closeEvent(self, event):  # type: ignore[override]
        # Salva tamanho e posição
        try:
            from app_settings import settings
            # Captura fator de zoom atual (primeiro QWebEngineView encontrado) antes de salvar
            try:
                from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
                for panel_name in ('left_panel', 'right_panel'):
                    panel = getattr(self, panel_name, None)
                    if not panel:
                        continue
                    views = panel.findChildren(QWebEngineView)
                    if views:
                        zf = views[0].zoomFactor()
                        if abs(getattr(settings, 'web_zoom_factor', 1.0) - zf) > 1e-6:
                            settings.web_zoom_factor = float(zf)
                        break
            except Exception:
                pass
            settings.win_size = [self.width(), self.height()]
            pos = self.pos()
            settings.win_pos = [pos.x(), pos.y()]
            if hasattr(self, 'splitter'):
                settings.splitter_sizes = self.splitter.sizes()
            settings.save()
        except Exception:
            pass
        super().closeEvent(event)

    # --- Ícone ---
    def _apply_window_icon(self):
        try:
            icon = self._create_book_icon()
            self.setWindowIcon(icon)
            if hasattr(self, 'windowHandle'):
                pass
            AmadonLogging.debug(self, _("log.icon.applied"))
        except Exception as e:  # pragma: no cover - apenas fallback visual
            AmadonLogging.warning(self, _("log.icon.failed").format(erro=e))

    def _create_book_icon(self) -> QIcon:
        size = 128
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        halo_grad = QLinearGradient(0, 0, 0, size)
        halo_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
        halo_grad.setColorAt(0.5, QColor(90, 120, 200, 30))
        halo_grad.setColorAt(1.0, QColor(40, 60, 120, 60))
        painter.setBrush(QBrush(halo_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(size*0.08, size*0.08, size*0.84, size*0.84)
        left_grad = QLinearGradient(size*0.15, size*0.2, size*0.48, size*0.85)
        left_grad.setColorAt(0.0, QColor(250, 250, 252))
        left_grad.setColorAt(1.0, QColor(225, 228, 235))
        right_grad = QLinearGradient(size*0.52, size*0.2, size*0.85, size*0.85)
        right_grad.setColorAt(0.0, QColor(250, 250, 252))
        right_grad.setColorAt(1.0, QColor(225, 228, 235))
        border_pen = QPen(QColor(40, 70, 140))
        border_pen.setWidth(3)
        painter.setPen(border_pen)
        painter.setBrush(QBrush(left_grad))
        painter.drawRoundedRect(int(size*0.14), int(size*0.18), int(size*0.34), int(size*0.60), 6, 6)
        painter.setBrush(QBrush(right_grad))
        painter.drawRoundedRect(int(size*0.52), int(size*0.18), int(size*0.34), int(size*0.60), 6, 6)
        center_pen = QPen(QColor(60, 90, 160))
        center_pen.setWidth(4)
        painter.setPen(center_pen)
        painter.drawLine(int(size*0.50), int(size*0.18), int(size*0.50), int(size*0.78))
        text_pen = QPen(QColor(90, 110, 160))
        text_pen.setWidth(2)
        painter.setPen(text_pen)
        for i in range(5):
            y = int(size*0.25 + i*size*0.07)
            painter.drawLine(int(size*0.18), y, int(size*0.44), y)
            painter.drawLine(int(size*0.56), y, int(size*0.82), y)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(200, 50, 60, 230))
        marker_x = int(size*0.47)
        marker_w = int(size*0.06)
        marker_y = int(size*0.12)
        marker_h = int(size*0.25)
        painter.drawRect(marker_x, marker_y, marker_w, marker_h)
        from PySide6.QtGui import QPainterPath
        tri_top = marker_y + marker_h
        path = QPainterPath()
        path.moveTo(marker_x, tri_top)
        path.lineTo(marker_x + marker_w, tri_top)
        path.lineTo(marker_x + marker_w/2, tri_top + int(size*0.07))
        path.closeSubpath()
        painter.drawPath(path)
        painter.end()
        return QIcon(pm)

    # --- Key events (fallback para garantir F11) ---
    def keyPressEvent(self, event):  # type: ignore[override]
        try:
            if event.key() == Qt.Key.Key_F11:
                # Garante toggle mesmo se QShortcut não disparar (ex.: foco interno WebEngine)
                self._toggle_focus_mode()
                event.accept()
                return
        except Exception:
            pass
        super().keyPressEvent(event)


# Variável global que conterá a instância única da janela principal
main_window: Optional[MainWindow] = None


def main() -> MainWindow:
    """Cria (se ainda não existir) e retorna a instância global de MainWindow."""
    global main_window
    if main_window is None:
        main_window = MainWindow()
    return main_window
