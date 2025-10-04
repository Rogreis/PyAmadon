from dataclasses import dataclass, asdict
from pathlib import Path
import json


SETTINGS_FILE = Path('settings.json')


@dataclass
class AppSettings:
    """Configurações globais simples com persistência JSON.

    Campos:
      dark_mode: tema escuro habilitado
      win_size: [largura, altura]
      win_pos: [x, y]
      last_module: último módulo aberto (ex.: 'documentos')
    """
    dark_mode: bool = False
    win_size: list | None = None
    win_pos: list | None = None
    last_module: str = ""
    splitter_sizes: list | None = None
    font_family: str = "Segoe UI"  # nova configuração de fonte preferida para leitura
    web_zoom_factor: float = 1.0  # fator de zoom (tamanho de fonte) para visores WebEngine

    def toggle_dark_mode(self):  # pragma: no cover (UI toggle futuro)
        self.dark_mode = not self.dark_mode

    # --- Persistência ---
    @classmethod
    def load(cls) -> 'AppSettings':
        if SETTINGS_FILE.exists():
            try:
                data = json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
                filtered = {k: v for k, v in data.items() if k in cls.__annotations__}
                return cls(**filtered)
            except Exception:
                pass
        return cls()

    def save(self):  # pragma: no cover - E/S simples
        try:
            SETTINGS_FILE.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception:
            pass

    # --- Tema global ---
    def global_stylesheet(self) -> str:
        font = self.font_family or 'Segoe UI'
        if self.dark_mode:
            return f"""\
QWidget {{ background-color:#121212; color:#e0e0e0; font-family:{font}; }}
QMainWindow, QDialog {{ background-color:#121212; }}
QStatusBar {{ background:#1e1e1e; border-top:1px solid #2a2a2a; }}
QLineEdit, QTreeWidget, QTextEdit {{ background:#1e1e1e; color:#f0f0f0; border:1px solid #3a3a3a; }}
QToolTip {{ background:#2a2a2a; color:#f0f0f0; border:1px solid #444; }}
QPushButton {{ background:#1565c0; color:#fff; border:1px solid #0d47a1; padding:4px 10px; border-radius:4px; }}
QPushButton:hover {{ background:#1e88e5; }}
QPushButton:pressed {{ background:#0d47a1; }}
QSplitter::handle {{ background:#2a2a2a; }}
QTreeView::item {{ padding:2px 4px; }}
QTreeView::item:selected {{ background:#264f78; color:#ffffff; }}
QTreeView::item:hover {{ background:#1b3d5c; }}
QWidget#LeftPanel, QWidget#RightPanel {{ background:#181a1c; }}
QWidget#LeftPanel:empty, QWidget#RightPanel:empty {{ background:#181a1c; }}
QLabel#StatusCurtoLabel {{ color:#bbbbbb; font-style:italic; padding:0 4px; margin-right:8px; }}
QLabel#StatusLongoLabel {{ color:#b0b0b0; font-style:italic; padding:0 4px; margin-right:12px; }}
QLabel#StatusPrincipalLabel {{ padding:2px 6px; }}
QLabel#LeftPanelPlaceholder {{ font-weight:bold; color:#e0e0e0; }}
QLabel#CenterPanelPlaceholder {{ font-size:15px; color:#e0e0e0; }}
"""
        else:
            return f"""\
QWidget {{ background-color:#f5f7fa; color:#1d1d1d; font-family:{font}; }}
QMainWindow, QDialog {{ background-color:#f5f7fa; }}
QStatusBar {{ background:#e7edf5; border-top:1px solid #c2cbd6; }}
QLineEdit, QTreeWidget, QTextEdit {{ background:#ffffff; color:#1d1d1d; border:1px solid #cbd3df; }}
QToolTip {{ background:#ffffff; color:#1d1d1d; border:1px solid #cbd3df; }}
QPushButton {{ background:#1565c0; color:#fff; border:1px solid #0d47a1; padding:4px 10px; border-radius:4px; }}
QPushButton:hover {{ background:#1e88e5; }}
QPushButton:pressed {{ background:#0d47a1; }}
QSplitter::handle {{ background:#0a3d7a; }}
QTreeView::item {{ padding:2px 4px; }}
QTreeView::item:selected {{ background:#1565c0; color:#ffffff; }}
QTreeView::item:hover {{ background:#0f4d92; }}
QWidget#LeftPanel, QWidget#RightPanel {{ background:#f0f4f8; }}
QWidget#LeftPanel:empty, QWidget#RightPanel:empty {{ background:#f0f4f8; }}
QLabel#StatusCurtoLabel {{ color:#5a5a5a; font-style:italic; padding:0 4px; margin-right:8px; }}
QLabel#StatusLongoLabel {{ color:#4a4a4a; font-style:italic; padding:0 4px; margin-right:12px; }}
QLabel#StatusPrincipalLabel {{ padding:2px 6px; }}
QLabel#LeftPanelPlaceholder {{ font-weight:bold; color:#103a60; }}
QLabel#CenterPanelPlaceholder {{ font-size:15px; color:#0a3d7a; }}
"""


# Instância global carregada ao importar módulo (safe: arquivo pequeno)
settings = AppSettings.load()

def apply_global_theme(app):  # pragma: no cover (UI)
    try:
        app.setStyleSheet(settings.global_stylesheet())
    except Exception:
        pass
