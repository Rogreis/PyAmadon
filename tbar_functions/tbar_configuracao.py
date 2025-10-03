from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QCheckBox, QMessageBox
from PySide6.QtCore import Qt
from app_settings import settings, apply_global_theme

class ToolBar_Configuracao(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.configuracao")
        self._status_curto("status.curto.cfg")
        self._status_principal("status.msg.configuracao")
        # Abre janela modal de configuração (placeholder)
        if self.context is not None:
            try:
                dialog = QDialog(self.context)
                dialog.setWindowTitle(_("toolbar.configuracao"))
                dialog.setModal(True)
                dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
                layout = QVBoxLayout(dialog)
                lbl = QLabel(_("status.msg.configuracao"), dialog)
                lbl.setWordWrap(True)
                layout.addWidget(lbl)

                # Checkbox Dark Mode
                chk_dark = QCheckBox(_("config.darkmode.label"), dialog)
                chk_dark.setChecked(settings.dark_mode)
                layout.addWidget(chk_dark)
                desc = QLabel(_("config.darkmode.desc"), dialog)
                desc.setStyleSheet("font-size:11px;color:#666;")
                desc.setWordWrap(True)
                layout.addWidget(desc)

                # Botões
                btn_apply = QPushButton(_("config.apply"), dialog)
                btn_close = QPushButton(_("config.close"), dialog)

                def apply_changes():
                    changed = False
                    if chk_dark.isChecked() != settings.dark_mode:
                        settings.dark_mode = chk_dark.isChecked()
                        # Reaplica tema global
                        from PySide6.QtWidgets import QApplication
                        app = QApplication.instance()
                        if app:
                            apply_global_theme(app)
                        changed = True
                    if changed:
                        settings.save()
                        QMessageBox.information(dialog, _("config.applied.title"), _("config.applied.msg"))

                btn_apply.clicked.connect(apply_changes)
                btn_close.clicked.connect(dialog.accept)
                layout.addWidget(btn_apply)
                layout.addWidget(btn_close)
                dialog.resize(420, 240)
                dialog.exec()
            except Exception:
                # Se algo falhar (ex.: ambiente headless), apenas segue.
                pass
        # Também mostra HTML no painel esquerdo
                body = f"""
                <div class='p-3'>
                    <h2>{_("html.config.title")}</h2>
                    <p>{_("html.config.intro")}</p>
                    <p><i>Diálogo modal aberto para ajustes gerais.</i></p>
                    <ul>
                        <li>Layout</li>
                        <li>Idioma</li>
                        <li>Fonte</li>
                        <li>Temas futuros</li>
                    </ul>
                </div>
                """
                self.inject_web_content(body, target='left', css="body{font-family:'Segoe UI';color:#124;} h2{color:#0a3d7a;border-bottom:1px solid #cbd3df;margin-top:0;} ul{padding-left:18px;} li{margin:3px 0;}")
        return _("status.msg.configuracao")