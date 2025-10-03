"""Módulo contendo a classe principal da janela da aplicação Amadon.

Expõe uma variável global `main_window` que conterá a instância única de `MainWindow`
após a chamada da função `main()` deste módulo.
"""
from __future__ import annotations

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
from PySide6.QtGui import QAction, QIcon, QPainter, QPen, QBrush, QColor, QLinearGradient, QPixmap

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
        self.resize(800, 600)
        AmadonLogging.debug(self, _("log.window.ready"))
        # Área central agora é um splitter horizontal (30% / 70%)
        self._criar_area_central()

        # --- Barra de Status ---
        self.status_curto = QLabel(_("status.pronto"))
        self.status_curto.setFixedWidth(80)
        self.status_curto.setStyleSheet(
            "QLabel { color: #5a5a5a; font-style: italic; padding: 0 4px; margin-right: 8px; }"
        )
        self.status_longo = QLabel(_("status.sistema_inicializado"))
        self.status_longo.setFixedWidth(200)
        self.status_longo.setStyleSheet(
            "QLabel { color: #4a4a4a; font-style: italic; padding: 0 4px; margin-right: 12px; }"
        )

        self.statusBar().addWidget(self.status_curto)
        self.statusBar().addWidget(self.status_longo)

        self.status_msg = ElidedLabel(
            _("app.title"),
            elide_mode=Qt.TextElideMode.ElideRight
        )
        self.status_msg.setStyleSheet("QLabel { padding: 2px 6px; }")
        self.statusBar().addPermanentWidget(self.status_msg, 1)

        # Constrói menus e toolbar específicos da aplicação
        self._criar_menus_e_toolbar()

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

        # Painel esquerdo (30%)
        left = QWidget(splitter)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(6, 6, 6, 6)
        left_layout.setSpacing(4)
        left_label = QLabel(_("placeholder.left.panel"), left)
        left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_label.setStyleSheet("QLabel { font-weight: bold; color: #103a60; }")
        left_layout.addWidget(left_label)

        # Painel direito (70%)
        right = QWidget(splitter)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(6, 6, 6, 6)
        right_layout.setSpacing(4)
        msg = QLabel(_("placeholder.center.message"), right)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("QLabel { font-size: 15px; color: #0a3d7a; }")
        right_layout.addWidget(msg)

        splitter.addWidget(left)
        splitter.addWidget(right)

        # Guarda referências se necessário futuramente
        self.splitter = splitter
        self.left_panel = left
        self.right_panel = right

        # Estilo do handle para ficar mais visível
        splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: #0a3d7a;
                border: 1px solid #082b52;
                margin: 0px;
            }
            QSplitter::handle:hover {
                background-color: #1565c0;
            }
            QSplitter::handle:pressed {
                background-color: #0d47a1;
            }
            """
        )

        self.setCentralWidget(splitter)

        # Ajusta proporções iniciais após o layout estar pronto
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: splitter.setSizes(self._calc_split_sizes()))

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
        toolbar.setIconSize(QSize(32, 32))
        # Mostra ícone + texto (texto abaixo do ícone)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        # Ações na ordem desejada
        toolbar.addAction(self._action_documentos)
        toolbar.addAction(self._action_assuntos)
        toolbar.addAction(self._action_artigos)
        toolbar.addSeparator()
        toolbar.addAction(self._action_busca)
        toolbar.addSeparator()
        toolbar.addAction(self._action_config)
        toolbar.addAction(self._action_ajuda)

        # Estilização: fundo azul, texto branco grande e negrito, mudança em hover
        toolbar.setStyleSheet(
            """
            QToolBar {
                background: #0a3d7a; /* Azul profundo de base */
                border: 0px;
                spacing: 4px;
                padding: 4px 6px;
            }
            QToolBar QToolButton {
                background-color: #1565c0; /* Azul médio */
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
                padding: 6px 10px 4px 10px;
                border-radius: 6px;
                margin: 2px;
                /* remove borda visual extra */
                border: 1px solid rgba(255,255,255,25);
            }
            QToolBar QToolButton:hover {
                background-color: #1e88e5; /* Azul mais claro no hover */
                color: #fffbf0; /* Leve tom quente */
                border: 1px solid rgba(255,255,255,60);
            }
            QToolBar QToolButton:pressed {
                background-color: #0d47a1; /* Azul escuro pressionado */
                color: #ffffff;
                border: 1px solid rgba(255,255,255,90);
            }
            QToolBar QToolButton:checked {
                background-color: #0b5599; /* Estado marcado */
                color: #ffffff;
                border: 1px solid rgba(255,255,255,120);
            }
            """
        )

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
        ToolBar_Documentos(self).GenerateData()

    def _abrir_assuntos(self):
        ToolBar_Assuntos(self).GenerateData()

    def _abrir_artigos(self):
        ToolBar_Artigos(self).GenerateData()

    def _abrir_busca(self):
        ToolBar_Busca(self).GenerateData()

    def _abrir_configuracao(self):
        ToolBar_Configuracao(self).GenerateData()

    def _abrir_ajuda(self):
        ToolBar_Ajuda(self).GenerateData()

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


# Variável global que conterá a instância única da janela principal
main_window: Optional[MainWindow] = None


def main() -> MainWindow:
    """Cria (se ainda não existir) e retorna a instância global de MainWindow."""
    global main_window
    if main_window is None:
        main_window = MainWindow()
    return main_window
