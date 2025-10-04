from tbar_functions.tbar_0base import ToolBar_Base
from i18n import _
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QCheckBox, QMessageBox
from PySide6.QtWidgets import QComboBox, QHBoxLayout
from PySide6.QtCore import Qt
from app_settings import settings, apply_global_theme


class ToolBar_Configuracao(ToolBar_Base):
    def __init__(self, context=None):
        super().__init__(context)
        self._log_info("log.open.configuracao")
        self._status_curto("status.curto.cfg")
        self._status_principal("status.msg.configuracao")
        # Conteúdo informativo para painel (HTML somente gerado em GenerateData)
        self._left_css = "body{font-family:'Segoe UI';color:#124;} h2{color:#0a3d7a;border-bottom:1px solid #cbd3df;margin-top:0;} ul{padding-left:18px;} li{margin:3px 0;}"
        # Lista de fontes sugeridas (pode evoluir para leitura dinâmica do sistema)
        # Lista base existente permanece dinâmica; adicionaremos Lato e Roboto Condensed se carregadas
        base_fonts = [
            "Segoe UI", "Arial", "Calibri", "Georgia", "Verdana",
            "Tahoma", "Times New Roman", "Trebuchet MS", "Noto Sans", "Open Sans"
        ]
        # Apenas adiciona novas fontes se disponíveis localmente (previamente carregadas em main)
        # Garante presença de Lato e Roboto Condensed na lista (serão carregadas em main se arquivos forem adicionados)
        self._font_options = base_fonts + ["Lato", "Roboto Condensed"]
        # Ordena alfabeticamente (case-insensitive) e remove duplicatas preservando ordem original antes do sort via dict
        self._font_options = sorted(dict.fromkeys(self._font_options), key=lambda s: s.lower())

    def GenerateData(self) -> str:  # noqa: N802
        # Apenas gera HTML (não abre diálogo, não injeta)
        body = f"""
        <div class='p-3'>
            <h2>{_("html.config.title")}</h2>
            <p>{_("html.config.intro")}</p>
            <p><i>Use o botão de configuração para alterar preferências.</i></p>
            <ul>
                <li>Layout</li>
                <li>Idioma</li>
                <li>Fonte</li>
                <li>Temas futuros</li>
            </ul>
        </div>
        """
        return body

    def Show(self):  # noqa: N802
        if self.context is None:
            return
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

            def _instant_toggle(state: int):
                desired = state == 2
                if desired != settings.dark_mode:
                    settings.dark_mode = desired
                    from PySide6.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app:
                        apply_global_theme(app)
                        try:
                            if hasattr(self.context, '_update_embedded_docs_theme'):
                                self.context._update_embedded_docs_theme()
                        except Exception:
                            pass
                    settings.save()

            chk_dark.stateChanged.connect(_instant_toggle)  # type: ignore
            desc = QLabel(_("config.darkmode.desc"), dialog)
            desc.setStyleSheet("font-size:11px;color:#666;")
            desc.setWordWrap(True)
            layout.addWidget(desc)

            # --- Seleção de Fonte ---
            font_label = QLabel(_("config.font.label"), dialog)
            font_label.setStyleSheet("margin-top:8px;font-weight:bold;")
            layout.addWidget(font_label)
            font_row = QHBoxLayout()
            cmb_font = QComboBox(dialog)
            for f in self._font_options:
                cmb_font.addItem(f)
            # Seleciona fonte atual
            try:
                idx = self._font_options.index(settings.font_family)
                cmb_font.setCurrentIndex(idx)
            except Exception:
                pass
            font_row.addWidget(cmb_font, 1)
            layout.addLayout(font_row)
            font_desc = QLabel(_("config.font.desc"), dialog)
            font_desc.setStyleSheet("font-size:11px;color:#666;")
            font_desc.setWordWrap(True)
            layout.addWidget(font_desc)

            def _apply_font_change(new_font: str):
                changed = new_font != settings.font_family
                settings.font_family = new_font
                # Reaplica stylesheet global
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    apply_global_theme(app)
                # Atualiza webviews existentes com JS que altera body font-family
                try:
                    if hasattr(self.context, 'left_panel') and self.context.left_panel:
                        self._update_webview_font(self.context.left_panel, new_font)
                    if hasattr(self.context, 'right_panel') and self.context.right_panel:
                        self._update_webview_font(self.context.right_panel, new_font)
                except Exception:
                    pass
                settings.save()
                if changed:
                    from mensagens import AmadonLogging
                    try:
                        AmadonLogging.info(self.context, _("config.font.applied").format(font=new_font))
                    except Exception:
                        pass

            def on_font_change(index: int):  # noqa: ARG001
                fnt = cmb_font.currentText().strip()
                if fnt:
                    _apply_font_change(fnt)
            cmb_font.currentIndexChanged.connect(on_font_change)  # type: ignore

            # Removido botão Aplicar (aplicação imediata). Mantém apenas Fechar.
            btn_close = QPushButton(_("config.close"), dialog)
            btn_close.clicked.connect(dialog.accept)
            layout.addWidget(btn_close)
            dialog.resize(420, 240)
            dialog.exec()
        except Exception:
            pass

    def _update_webview_font(self, panel, font):
        """Aplica fonte às instâncias de QWebEngineView já carregadas."""
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
        except Exception:
            return
        js = f"""
        (function(){{
            try {{
                document.body.style.fontFamily = '{font}';
                const all = document.querySelectorAll('.markdown-body, .doc-body');
                all.forEach(el => el.style.fontFamily = '{font}');
            }} catch(e){{}}
        }})();
        """
        for view in panel.findChildren(QWebEngineView):
            try:
                view.page().runJavaScript(js)
            except Exception:
                pass

    def css_left(self):
        return getattr(self, '_left_css', None)