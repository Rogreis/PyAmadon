import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Minha Aplicação com Menus")
        self.resize(800, 600)

        # Widget central
        label = QLabel("Use o menu ou a barra de ferramentas.", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)

        # --- Barra de Status ---
        # A barra de status é criada automaticamente, só precisamos acessá-la
        self.statusBar().showMessage("Pronto.", 3000) # Mensagem e timeout (ms)

        # --- Ações (Actions) ---
        # Ações são comandos que podem ser usados em menus, toolbars, etc.
        action_nova = QAction(QIcon.fromTheme("document-new"), "&Novo", self)
        action_nova.setStatusTip("Criar um novo arquivo")
        action_nova.triggered.connect(self.on_novo_arquivo)

        action_sair = QAction(QIcon.fromTheme("application-exit"), "&Sair", self)
        action_sair.setStatusTip("Fechar a aplicação")
        action_sair.triggered.connect(self.close) # self.close é um slot padrão

        # --- Barra de Menu ---
        menu_bar = self.menuBar()
        menu_arquivo = menu_bar.addMenu("&Arquivo")
        menu_arquivo.addAction(action_nova)
        menu_arquivo.addSeparator()
        menu_arquivo.addAction(action_sair)

        # --- Barra de Ferramentas (Toolbar) ---
        toolbar = QToolBar("Barra de Ferramentas Principal")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        toolbar.addAction(action_nova)
        toolbar.addAction(action_sair)

    # Slots (métodos que respondem a sinais/eventos)
    def on_novo_arquivo(self):
        print("Ação: 'Novo Arquivo' foi acionada!")
        self.statusBar().showMessage("Novo arquivo criado (simulado).", 3000)
        # O widget central poderia ser atualizado aqui
        self.centralWidget().setText("Um novo arquivo foi iniciado!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
