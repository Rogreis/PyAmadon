"""Módulo contendo a classe principal da janela da aplicação Amadon.

Expõe uma variável global `main_window` que conterá a instância única de `MainWindow`
após a chamada da função `main()` deste módulo.
"""
from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtWidgets import QMainWindow, QLabel, QToolBar, QSizePolicy
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QPainter, QPen, QBrush, QColor, QLinearGradient, QPixmap

from mensagens import MensagensStatus, AmadonLogging

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
        AmadonLogging.info(self, "Iniciando aplicação Amadon")
        self._apply_window_icon()

        self.setWindowTitle("Amadon - Leitura e estudo do Livro de Urântia")
        self.resize(800, 600)
        AmadonLogging.debug(self, "Janela principal configurada")

        label = QLabel("Use o menu ou a barra de ferramentas.", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)

        # --- Barra de Status ---
        self.status_curto = QLabel("Pronto")
        self.status_curto.setFixedWidth(80)
        self.status_curto.setStyleSheet(
            "QLabel { color: #5a5a5a; font-style: italic; padding: 0 4px; margin-right: 8px; }"
        )

        self.status_longo = QLabel("Sistema inicializado")
        self.status_longo.setFixedWidth(200)
        self.status_longo.setStyleSheet(
            "QLabel { color: #4a4a4a; font-style: italic; padding: 0 4px; margin-right: 12px; }"
        )

        self.statusBar().addWidget(self.status_curto)
        self.statusBar().addWidget(self.status_longo)

        self.status_msg = ElidedLabel(
            "Amadon - Sistema de estudo do Livro de Urântia",
            elide_mode=Qt.TextElideMode.ElideRight
        )
        self.status_msg.setStyleSheet("QLabel { padding: 2px 6px; }")
        self.statusBar().addPermanentWidget(self.status_msg, 1)

        # --- Ações ---
        action_nova = QAction(QIcon.fromTheme("document-new"), "&Novo", self)
        action_nova.setStatusTip("Criar um novo arquivo")
        action_nova.triggered.connect(self.on_novo_arquivo)

        action_sair = QAction(QIcon.fromTheme("application-exit"), "&Sair", self)
        action_sair.setStatusTip("Fechar a aplicação")
        action_sair.triggered.connect(self.close)

        action_teste_status = QAction("&Testar Status", self)
        action_teste_status.setStatusTip("Testar os campos de status")
        action_teste_status.triggered.connect(self.on_testar_status)

        action_teste_logs = QAction("Testar &Logs", self)
        action_teste_logs.setStatusTip("Demonstrar diferentes níveis de log")
        action_teste_logs.triggered.connect(self.on_testar_logs)

        menu_bar = self.menuBar()
        menu_arquivo = menu_bar.addMenu("&Arquivo")
        menu_arquivo.addAction(action_nova)
        menu_arquivo.addSeparator()
        menu_arquivo.addAction(action_sair)

        menu_teste = menu_bar.addMenu("&Teste")
        menu_teste.addAction(action_teste_status)
        menu_teste.addAction(action_teste_logs)

        toolbar = QToolBar("Barra de Ferramentas Principal")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        toolbar.addAction(action_nova)
        toolbar.addAction(action_sair)

    # --- Logging ---
    def _setup_logger(self):
        if USE_ADVANCED_LOGGING:
            self.logger = AmadonLoggingConfig.setup_advanced_logging('Amadon')
            AmadonLogging.info(self, "Usando configuração avançada de logging")
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
        AmadonLogging.debug(self, "Status principal limpo")

    def atualizar_status_curto(self, texto: str):
        MensagensStatus.curto(self, texto)

    def atualizar_status_longo(self, texto: str):
        MensagensStatus.longo(self, texto)

    def set_status_mensagem(self, texto: str):
        MensagensStatus.principal(self, texto)

    def atualizar_ambos_status(self, curto: str, longo: str):
        MensagensStatus.ambos(self, curto, longo)

    # --- Ações ---
    def on_testar_status(self):
        from PySide6.QtCore import QTimer
        AmadonLogging.info(self, "Iniciando teste dos campos de status")
        QTimer.singleShot(2000, lambda: self._finalizar_teste_status())

    def _finalizar_teste_status(self):
        self.atualizar_ambos_status("OK", "Teste concluído com sucesso")
        AmadonLogging.info(self, "Teste dos campos de status concluído com sucesso")

    def on_testar_logs(self):
        AmadonLogging.debug(self, "Mensagem de DEBUG - informações detalhadas para desenvolvimento")
        AmadonLogging.info(self, "Mensagem de INFO - informações gerais sobre o funcionamento")
        AmadonLogging.warning(self, "Mensagem de WARNING - algo pode estar incorreto")
        AmadonLogging.error(self, "Mensagem de ERROR - erro que não impede a execução")
        try:
            _ = 10 / 0
        except ZeroDivisionError as e:
            # Usa novo método que recebe explicitamente a exception
            AmadonLogging.error_with_exception(self, "Erro simulado capturado", e)
        self.set_status_mensagem("Diferentes níveis de log foram registrados - verifique amadon.log")
        self.atualizar_status_curto("Log")
        self.atualizar_status_longo("Logs demonstrados")

    def on_novo_arquivo(self):
        AmadonLogging.info(self, "Ação 'Novo Arquivo' executada pelo usuário")
        self.atualizar_status_curto("Novo")
        self.atualizar_status_longo("Arquivo criado")
        self.set_status_mensagem("Novo arquivo criado (simulado).")
        self.centralWidget().setText("Um novo arquivo foi iniciado!")
        AmadonLogging.debug(self, "Interface atualizada após criação de novo arquivo")

    # --- Ícone ---
    def _apply_window_icon(self):
        try:
            icon = self._create_book_icon()
            self.setWindowIcon(icon)
            if hasattr(self, 'windowHandle'):
                pass
            AmadonLogging.debug(self, "Ícone de janela aplicado com sucesso")
        except Exception as e:  # pragma: no cover - apenas fallback visual
            AmadonLogging.warning(self, f"Falha ao aplicar ícone customizado: {e}")

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
