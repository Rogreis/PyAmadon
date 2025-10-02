import sys
import logging
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QSizePolicy
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QAction, QIcon, QPainter, QPen, QBrush, QColor, QLinearGradient, QPixmap

# Importa configuração avançada de logging (opcional)
try:
    from logging_config import AmalonLoggingConfig
    USE_ADVANCED_LOGGING = True
except ImportError:
    USE_ADVANCED_LOGGING = False

class ElidedLabel(QLabel):
    """QLabel que aplica elipse automática quando o texto não cabe."""
    def __init__(self, text="", parent=None, elide_mode=Qt.TextElideMode.ElideRight):
        super().__init__(text, parent)
        self._full_text = text
        self._elide_mode = elide_mode
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def setText(self, text: str):
        self._full_text = text
        super().setText(text)
        self._update_elided()

    def resizeEvent(self, event):
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

    def fullText(self):
        return self._full_text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuração do logger
        self._setup_logger()
        self.logger.info("Iniciando aplicação Amadon")

        # Aplica ícone customizado (livro) indicando estudo/leitura
        self._apply_window_icon()

        self.setWindowTitle("Amadon - Leitura e estudo do Livro de Urântia")
        self.resize(800, 600)
        self.logger.debug("Janela principal configurada")

        # Widget central
        label = QLabel("Use o menu ou a barra de ferramentas.", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)

        # --- Barra de Status ---
        # A barra de status é criada automaticamente, só precisamos acessá-la
        # Campo para mensagens curtas (uma palavra)
        self.status_curto = QLabel("Pronto")
        self.status_curto.setFixedWidth(80)
        # Estilo discreto: sem borda, itálico e cor levemente diferenciada
        self.status_curto.setStyleSheet(
            "QLabel { color: #5a5a5a; font-style: italic; padding: 0 4px; margin-right: 8px; }"
        )
        
        # Campo para mensagens longas
        self.status_longo = QLabel("Sistema inicializado")
        self.status_longo.setFixedWidth(200)
        self.status_longo.setStyleSheet(
            "QLabel { color: #4a4a4a; font-style: italic; padding: 0 4px; margin-right: 12px; }"
        )
        
        # Adiciona os campos à barra de status (à esquerda)
        self.statusBar().addWidget(self.status_curto)
        self.statusBar().addWidget(self.status_longo)

        # Mensagem principal expansível com elipse automática
        self.status_msg = ElidedLabel(
            "Amadon - Sistema de estudo do Livro de Urântia",
            elide_mode=Qt.TextElideMode.ElideRight
        )
        self.status_msg.setStyleSheet("QLabel { padding: 2px 6px; }")
        self.statusBar().addPermanentWidget(self.status_msg, 1)

        # --- Ações (Actions) ---
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

        # --- Barra de Menu ---
        menu_bar = self.menuBar()
        menu_arquivo = menu_bar.addMenu("&Arquivo")
        menu_arquivo.addAction(action_nova)
        menu_arquivo.addSeparator()
        menu_arquivo.addAction(action_sair)

        menu_teste = menu_bar.addMenu("&Teste")
        menu_teste.addAction(action_teste_status)
        menu_teste.addAction(action_teste_logs)

        # --- Barra de Ferramentas (Toolbar) ---
        toolbar = QToolBar("Barra de Ferramentas Principal")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        toolbar.addAction(action_nova)
        toolbar.addAction(action_sair)

    # Métodos para atualizar os campos de status
    def atualizar_status_curto(self, mensagem):
        """Atualiza o campo de status para mensagens curtas (uma palavra)"""
        self.status_curto.setText(str(mensagem))
        self.logger.debug(f"Status curto atualizado: {mensagem}")
    
    def atualizar_status_longo(self, mensagem):
        """Atualiza o campo de status para mensagens longas"""
        self.status_longo.setText(str(mensagem))
        self.logger.debug(f"Status longo atualizado: {mensagem}")
    
    def atualizar_ambos_status(self, curto, longo):
        """Atualiza ambos os campos de status simultaneamente"""
        self.atualizar_status_curto(curto)
        self.atualizar_status_longo(longo)
    
    def _setup_logger(self):
        """Configura o sistema de logging da aplicação"""
        if USE_ADVANCED_LOGGING:
            # Usa configuração avançada se disponível
            self.logger = AmalonLoggingConfig.setup_advanced_logging('Amadon')
            self.logger.info("Usando configuração avançada de logging")
        else:
            # Configuração básica
            self._setup_basic_logger()
    
    def _setup_basic_logger(self):
        """Configuração básica de logging"""
        # Cria o logger principal da aplicação
        self.logger = logging.getLogger('Amadon')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove handlers existentes para evitar duplicatas
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Formatter personalizado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para arquivo de log
        file_handler = logging.FileHandler('amadon.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler para console (útil durante desenvolvimento)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Adiciona os handlers ao logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Evita propagação para o logger raiz
        self.logger.propagate = False
    
    def set_status_mensagem(self, texto: str):
        """Atualiza a mensagem principal expansível da barra de status"""
        self.status_msg.setText(texto)
        self.logger.debug(f"Status principal atualizado: {texto}")

    def set_status_temporario(self, texto: str, ms: int = 3000):
        """Mostra uma mensagem temporária e restaura a anterior após timeout."""
        from PySide6.QtCore import QTimer
        anterior = self.status_msg.fullText()
        self.set_status_mensagem(texto)
        QTimer.singleShot(ms, lambda: self.set_status_mensagem(anterior))

    def clear_status_mensagem(self):
        """Limpa a mensagem principal"""
        self.status_msg.clear()
        self.logger.debug("Status principal limpo")

    def on_testar_status(self):
        """Método para testar os diferentes campos de status"""
        from PySide6.QtCore import QTimer
        
        self.logger.info("Iniciando teste dos campos de status")
        
        # Testa mensagens diferentes
        self.atualizar_status_curto("Teste")
        self.atualizar_status_longo("Testando campos de status")
        self.set_status_mensagem("Executando teste dos campos de status...")
        
        # Programa uma mudança após 2 segundos
        QTimer.singleShot(2000, lambda: self._finalizar_teste_status())
    
    def _finalizar_teste_status(self):
        """Finaliza o teste dos campos de status"""
        self.atualizar_ambos_status("OK", "Teste concluído com sucesso")
        self.logger.info("Teste dos campos de status concluído com sucesso")
    
    def on_testar_logs(self):
        """Demonstra os diferentes níveis de log disponíveis"""
        self.logger.debug("Mensagem de DEBUG - informações detalhadas para desenvolvimento")
        self.logger.info("Mensagem de INFO - informações gerais sobre o funcionamento")
        self.logger.warning("Mensagem de WARNING - algo pode estar incorreto")
        self.logger.error("Mensagem de ERROR - erro que não impede a execução")
        
        try:
            # Simula uma operação que pode falhar
            resultado = 10 / 0
        except ZeroDivisionError as e:
            self.logger.error(f"Erro simulado capturado: {e}")
        
        self.set_status_mensagem("Diferentes níveis de log foram registrados - verifique amadon.log")
        self.atualizar_status_curto("Log")
        self.atualizar_status_longo("Logs demonstrados")

    # Slots (métodos que respondem a sinais/eventos)
    def on_novo_arquivo(self):
        self.logger.info("Ação 'Novo Arquivo' executada pelo usuário")
        # Atualiza os campos de status específicos
        self.atualizar_status_curto("Novo")
        self.atualizar_status_longo("Arquivo criado")
        # Mensagem na barra principal
        self.set_status_mensagem("Novo arquivo criado (simulado).")
        # O widget central poderia ser atualizado aqui
        self.centralWidget().setText("Um novo arquivo foi iniciado!")
        self.logger.debug("Interface atualizada após criação de novo arquivo")

    # -------------------------------------------------
    # Ícone da aplicação (gerado dinamicamente)
    # -------------------------------------------------
    def _apply_window_icon(self):
        """Gera e aplica um ícone de 'livro' para representar estudo/leitura."""
        try:
            icon = self._create_book_icon()
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)
            self.logger.debug("Ícone de janela aplicado com sucesso")
        except Exception as e:
            self.logger.warning(f"Falha ao aplicar ícone customizado: {e}")

    def _create_book_icon(self) -> QIcon:
        """Cria um QIcon desenhando um livro estilizado.

        Desenho: duas páginas abertas com linha central e marcação superior simulando marcador.
        """
        size = 128
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pm)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Fundo leve (halo)
        halo_grad = QLinearGradient(0, 0, 0, size)
        halo_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
        halo_grad.setColorAt(0.5, QColor(90, 120, 200, 30))
        halo_grad.setColorAt(1.0, QColor(40, 60, 120, 60))
        painter.setBrush(QBrush(halo_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(size*0.08, size*0.08, size*0.84, size*0.84)

        # Páginas
        left_grad = QLinearGradient(size*0.15, size*0.2, size*0.48, size*0.85)
        left_grad.setColorAt(0.0, QColor(250, 250, 252))
        left_grad.setColorAt(1.0, QColor(225, 228, 235))

        right_grad = QLinearGradient(size*0.52, size*0.2, size*0.85, size*0.85)
        right_grad.setColorAt(0.0, QColor(250, 250, 252))
        right_grad.setColorAt(1.0, QColor(225, 228, 235))

        border_pen = QPen(QColor(40, 70, 140))
        border_pen.setWidth(3)
        painter.setPen(border_pen)

        # Página esquerda
        painter.setBrush(QBrush(left_grad))
        painter.drawRoundedRect(int(size*0.14), int(size*0.18), int(size*0.34), int(size*0.60), 6, 6)

        # Página direita
        painter.setBrush(QBrush(right_grad))
        painter.drawRoundedRect(int(size*0.52), int(size*0.18), int(size*0.34), int(size*0.60), 6, 6)

        # Linha central (dobra)
        center_pen = QPen(QColor(60, 90, 160))
        center_pen.setWidth(4)
        painter.setPen(center_pen)
        painter.drawLine(int(size*0.50), int(size*0.18), int(size*0.50), int(size*0.78))

        # "Texto" simulado (linhas finas)
        text_pen = QPen(QColor(90, 110, 160))
        text_pen.setWidth(2)
        painter.setPen(text_pen)
        for i in range(5):
            y = int(size*0.25 + i*size*0.07)
            painter.drawLine(int(size*0.18), y, int(size*0.44), y)
            painter.drawLine(int(size*0.56), y, int(size*0.82), y)

        # Marcador (bookmark)
        from PySide6.QtCore import QPoint
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(200, 50, 60, 230))
        marker_x = int(size*0.47)
        marker_w = int(size*0.06)
        marker_y = int(size*0.12)
        marker_h = int(size*0.25)
        painter.drawRect(marker_x, marker_y, marker_w, marker_h)
        # Triângulo inferior
        tri_top = marker_y + marker_h
        from PySide6.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(marker_x, tri_top)
        path.lineTo(marker_x + marker_w, tri_top)
        path.lineTo(marker_x + marker_w/2, tri_top + int(size*0.07))
        path.closeSubpath()
        painter.drawPath(path)

        painter.end()

        return QIcon(pm)


if __name__ == "__main__":
    # Configuração básica de logging antes da criação da aplicação
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Log de inicialização
    window.logger.info("Aplicação Amadon iniciada com sucesso")
    
    window.show()
    
    try:
        exit_code = app.exec()
        window.logger.info(f"Aplicação encerrada normalmente com código: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        window.logger.error(f"Erro durante execução da aplicação: {e}")
        sys.exit(1)
