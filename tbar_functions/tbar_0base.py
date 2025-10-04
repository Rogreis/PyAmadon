from abc import ABC, abstractmethod
from typing import Any
from i18n import _
from PySide6.QtWidgets import QWidget, QTextBrowser, QScrollArea, QVBoxLayout
from PySide6.QtCore import Qt

def _safe_logger():
    import logging
    return logging.getLogger('Amadon')

class ToolBar_Base(ABC):
    """Base para ações da toolbar.

    Recebe a janela principal em context. Fornece helpers para logging e
    atualização de status, permitindo que cada classe concreta concentre a
    lógica de interface e mensagens.
    """
    def __init__(self, context: Any | None = None) -> None:
        self.context = context

    # ---- Helpers ----
    def _log_info(self, key: str):
        try:
            from mensagens import AmadonLogging
            if self.context is not None:
                AmadonLogging.info(self.context, _(key))
            else:
                _safe_logger().info(_(key))
        except Exception:
            _safe_logger().info(_(key))

    def _log_debug(self, key: str):
        try:
            from mensagens import AmadonLogging
            if self.context is not None:
                AmadonLogging.debug(self.context, _(key))
            else:
                _safe_logger().debug(_(key))
        except Exception:
            _safe_logger().debug(_(key))

    def _status_curto(self, key: str):
        if self.context is None:
            return
        try:
            from mensagens import MensagensStatus
            MensagensStatus.curto(self.context, _(key))
        except Exception:
            pass

    def _status_longo(self, key: str):
        if self.context is None:
            return
        try:
            from mensagens import MensagensStatus
            MensagensStatus.longo(self.context, _(key))
        except Exception:
            pass

    def _status_principal(self, key: str):
        if self.context is None:
            return
        try:
            from mensagens import MensagensStatus
            MensagensStatus.principal(self.context, _(key))
        except Exception:
            pass

    # --- UI helpers ---
    def inject_widget(self, widget: QWidget, target: str = 'left', clear: bool = True):
        """Adiciona um widget ao painel indicado ('left' ou 'right').

        Agora, quando clear=True, TODOS os widgets existentes no painel são removidos
        (inclusive qualquer placeholder antigo). Isso garante que nenhum resquício
        visual permaneça antes de inserir novo conteúdo.

        Parameters
        ----------
        widget : QWidget
            O widget a ser inserido.
        target : str
            'left' ou 'right'; default 'left'.
        clear : bool
            Se True, limpa completamente o painel antes de adicionar.
        """
        if self.context is None:
            return
        panel = None
        if target == 'left':
            panel = getattr(self.context, 'left_panel', None)
        elif target == 'right':
            panel = getattr(self.context, 'right_panel', None)
        if panel is None:
            return
        layout = panel.layout()
        if layout is None:
            return
        if clear:
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.deleteLater()
        layout.addWidget(widget)

    def inject_html(
        self,
        html: str,
        target: str = 'left',
        clear: bool = True,
        wrap_in_scroll: bool = False,
        css: str | None = None,
    ) -> QWidget:
        """Convenience para injetar conteúdo HTML com rolagem.

        Usa QTextBrowser (já com scroll embutido). Se wrap_in_scroll=True, envolve
        o QTextBrowser em um QScrollArea adicional (normalmente desnecessário).

        Parameters
        ----------
        html : str
            Conteúdo HTML (subset Qt Rich Text) a renderizar.
        target : str
            'left' ou 'right'.
        clear : bool
            Se True limpa widgets anteriores (mantendo título).
        wrap_in_scroll : bool
            Envolve em QScrollArea extra; útil se quiser aplicar política
            de scroll externa customizada.
        css : str | None
            CSS inline adicional para aplicar no corpo (será injetado no <style>).
        """
        if css:
            html_final = f"<html><head><style>{css}</style></head><body>{html}</body></html>"
        else:
            html_final = html
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setReadOnly(True)
        browser.setHtml(html_final)
        browser.setStyleSheet(
            "QTextBrowser { background: #ffffff; border: 1px solid #c7d4e5; padding: 6px; }"
            "QScrollBar:vertical { width: 12px; background: #f0f4f8; }"
            "QScrollBar::handle:vertical { background: #90a4b8; border-radius: 5px; min-height: 20px; }"
            "QScrollBar::handle:vertical:hover { background: #6f8aa3; }"
            "QScrollBar::add-line, QScrollBar::sub-line { height: 0; }"
        )
        container: QWidget
        if wrap_in_scroll:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(browser)
            container = scroll
        else:
            container = browser
        self.inject_widget(container, target=target, clear=clear)
        return container

    def inject_web_content(
        self,
        body_html: str,
        target: str = 'left',
        clear: bool = True,
        css: str | None = None,
        js: str | None = None,
        external_css_urls: list[str] | None = None,
        external_js_urls: list[str] | None = None,
        use_bootstrap: bool = False,
        on_load_js: str | None = None,
    ):
        """Injeta conteúdo baseado em QWebEngineView com suporte a CSS/JS completos.

        Se QWebEngine não estiver disponível, faz fallback para inject_html.

        Parameters
        ----------
        body_html : str
            HTML do corpo (sem <html>/<head>/<body>) ou completo; será embrulhado.
        target : str
            'left' ou 'right'.
        css : str | None
            CSS interno adicional.
        js : str | None
            Script JavaScript inline (executado após carregar a página).
        external_css_urls : list[str]
            URLs de folhas de estilo externas (CDNs etc.).
        external_js_urls : list[str]
            URLs de scripts externos.
        use_bootstrap : bool
            Se True, injeta links CDN de Bootstrap 5 (CSS + bundle JS).
        on_load_js : str | None
            Código JS extra disparado após load (via runJavaScript).
        """
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
        except Exception:
            # Fallback simples
            merged = body_html
            if css:
                merged = f"<style>{css}</style>" + merged
            return self.inject_html(merged, target=target, clear=clear)

        # Detecta tema atual da aplicação (fallback light)
        try:
            from app_settings import settings as _settings
            is_dark = bool(getattr(_settings, 'dark_mode', False))
        except Exception:  # pragma: no cover
            is_dark = False

        theme_css = (
            """
            /* Tema base para documentos embedados */
            body.doc-body { margin:0; padding:16px 18px 40px 18px; font-family: system-ui, Arial, sans-serif; line-height:1.5; min-height:100%; }
            body.doc-theme-light { background:#ffffff; color:#1d1d1d; }
            body.doc-theme-dark { background:#121212; color:#e0e0e0; }
            body.doc-body h1 { font-size:1.9em; margin:0.4em 0 0.6em; font-weight:600; }
            body.doc-body h2 { font-size:1.45em; margin:1.2em 0 0.5em; font-weight:600; }
            body.doc-body h3 { font-size:1.18em; margin:1em 0 0.4em; font-weight:600; }
            body.doc-body p { margin:0 0 0.85em; }
            body.doc-body a { text-decoration:none; }
            body.doc-theme-light a { color:#0d47a1; }
            body.doc-theme-light a:hover { text-decoration:underline; }
            body.doc-theme-dark a { color:#64b5f6; }
            body.doc-theme-dark a:hover { text-decoration:underline; }
            body.doc-body code { font-family: Consolas, 'Courier New', monospace; font-size:0.95em; }
            body.doc-theme-light code { background:#f0f2f5; color:#222; padding:2px 5px; border-radius:4px; }
            body.doc-theme-dark code { background:#1e1e1e; color:#eee; padding:2px 5px; border-radius:4px; }
            body.doc-theme-light pre { background:#f5f7fa; color:#1d1d1d; border:1px solid #d0d7e2; }
            body.doc-theme-dark pre { background:#272822; color:#eee; border:1px solid #3a3f42; }
            body.doc-body pre { padding:10px 12px; border-radius:8px; overflow:auto; }
            body.doc-body table { border-collapse: collapse; margin:1em 0; }
            body.doc-theme-light table th, body.doc-theme-light table td { border:1px solid #c7d4e5; }
            body.doc-theme-dark table th, body.doc-theme-dark table td { border:1px solid #3a3f42; }
            body.doc-body table th, body.doc-body table td { padding:6px 10px; font-size:0.92em; }
            body.doc-body hr { border:none; height:1px; background:linear-gradient(to right, transparent, #888, transparent); margin:2em 0; }
            body.doc-theme-dark hr { background:linear-gradient(to right, transparent, #444, transparent); }
            body.doc-body blockquote { margin:1em 0; padding:8px 14px; border-left:4px solid #1565c0; border-radius:4px; }
            body.doc-theme-light blockquote { background:#f0f5fb; color:#1d1d1d; }
            body.doc-theme-dark blockquote { background:#1e1e24; color:#e0e0e0; border-left-color:#90caf9; }
            body.doc-body .anchor-highlight { animation: anchorFlash 2.2s ease-in-out 1; }
            @keyframes anchorFlash { 0% { box-shadow:0 0 0 0 rgba(255,215,0,0.9);} 60% { box-shadow:0 0 0 10px rgba(255,215,0,0);} 100% { box-shadow:0 0 0 0 rgba(255,215,0,0);} }
            /* Scrollbar custom leve */
            body.doc-theme-dark ::-webkit-scrollbar { width:10px; }
            body.doc-theme-dark ::-webkit-scrollbar-track { background:#1e1e1e; }
            body.doc-theme-dark ::-webkit-scrollbar-thumb { background:#3a3f42; border-radius:6px; }
            body.doc-theme-dark ::-webkit-scrollbar-thumb:hover { background:#4a5054; }
            body.doc-theme-light ::-webkit-scrollbar { width:10px; }
            body.doc-theme-light ::-webkit-scrollbar-track { background:#f0f2f5; }
            body.doc-theme-light ::-webkit-scrollbar-thumb { background:#c1ccd6; border-radius:6px; }
            body.doc-theme-light ::-webkit-scrollbar-thumb:hover { background:#a5b2bd; }
            """
        )

        head_parts: list[str] = [f"<style>{theme_css}</style>"]
        if use_bootstrap:
            head_parts.append(
                "<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css\" integrity=\"sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH\" crossorigin=\"anonymous\">"
            )
        if external_css_urls:
            for url in external_css_urls:
                head_parts.append(f"<link rel=\"stylesheet\" href=\"{url}\">")
        if css:
            head_parts.append(f"<style>{css}</style>")

        script_tail: list[str] = []
        if use_bootstrap:
            script_tail.append(
                "<script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js\" integrity=\"sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz\" crossorigin=\"anonymous\"></script>"
            )
        if external_js_urls:
            for url in external_js_urls:
                script_tail.append(f"<script src=\"{url}\"></script>")
        if js:
            script_tail.append(f"<script>{js}</script>")

        theme_class = 'doc-theme-dark' if is_dark else 'doc-theme-light'
        transition_css = """
        <style>
        body.doc-body { opacity:0; transition: opacity .28s ease-in; }
        body.doc-body.doc-loaded { opacity:1; }
        #__doc_loading_placeholder {position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-family:system-ui,Arial,sans-serif; font-size:14px; color:#888; letter-spacing:.5px;}
        body.doc-theme-dark #__doc_loading_placeholder { color:#aaa; }
        .doc-spinner { width:42px; height:42px; border:4px solid rgba(120,140,160,0.35); border-top-color:#1565c0; border-radius:50%; animation:spin 0.9s linear infinite; margin-bottom:12px; }
        body.doc-theme-dark .doc-spinner { border:4px solid rgba(255,255,255,0.18); border-top-color:#64b5f6; }
        @keyframes spin { to { transform:rotate(360deg); } }
        </style>
        """
        on_dom_loaded = """
        <script>
        document.addEventListener('DOMContentLoaded',()=>{
            document.body.classList.add('doc-loaded');
            const ph=document.getElementById('__doc_loading_placeholder');
            if(ph){ ph.style.opacity='0'; setTimeout(()=>ph.remove(),300); }
        });
        </script>
        """
        full_html = (
            "<html><head>"
            + "".join(head_parts)
            + transition_css
            + f"</head><body class='doc-body {theme_class}'>"
            + "<div id='__doc_loading_placeholder'><div style='text-align:center'><div class='doc-spinner'></div><div>Carregando...</div></div></div>"
            + body_html
            + "".join(script_tail)
            + on_dom_loaded
            + "</body></html>"
        )

        # Subclasse com suporte a persistência de zoom
        try:
            from app_settings import settings as _settings
        except Exception:  # pragma: no cover
            _settings = None

        outer_context = self.context
        from i18n import _ as _tr

        class AmadonWebView(QWebEngineView):  # type: ignore
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                # Aplica fator salvo
                if _settings is not None:
                    try:
                        self.setZoomFactor(float(getattr(_settings, 'web_zoom_factor', 1.0)))
                    except Exception:
                        pass

            def wheelEvent(self, event):  # type: ignore[override]
                try:
                    if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                        delta = event.angleDelta().y()
                        step = 0.1
                        z = self.zoomFactor()
                        if delta > 0:
                            z += step
                        elif delta < 0:
                            z -= step
                        z = max(0.6, min(1.8, round(z, 2)))
                        self.setZoomFactor(z)
                        if _settings is not None:
                            _settings.web_zoom_factor = float(z)
                            try:
                                _settings.save()
                            except Exception:
                                pass
                        try:
                            import logging
                            logging.getLogger('Amadon').debug(f"Zoom atualizado via wheel para {z}")
                        except Exception:
                            pass
                        # Mostra na barra de status (temporário)
                        try:
                            if outer_context is not None:
                                from mensagens import MensagensStatus
                                MensagensStatus.temporario_principal(outer_context, _tr("zoom.display").format(factor=f"{z:.1f}"), 1500)
                        except Exception:
                            pass
                        event.accept()
                        return
                except Exception:
                    pass
                super().wheelEvent(event)

            def keyPressEvent(self, event):  # type: ignore[override]
                handled = False
                try:
                    if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                        key = event.key()
                        z = self.zoomFactor()
                        if key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):  # Ctrl + '+'
                            z = min(1.8, round(z + 0.1, 2))
                            handled = True
                        elif key == Qt.Key.Key_Minus:
                            z = max(0.6, round(z - 0.1, 2))
                            handled = True
                        elif key in (Qt.Key.Key_0, Qt.Key.Key_Zero):
                            z = 1.0
                            handled = True
                        if handled:
                            self.setZoomFactor(z)
                            if _settings is not None:
                                _settings.web_zoom_factor = float(z)
                                try:
                                    _settings.save()
                                except Exception:
                                    pass
                            try:
                                import logging
                                logging.getLogger('Amadon').debug(f"Zoom atualizado via teclado para {z}")
                            except Exception:
                                pass
                            try:
                                if outer_context is not None:
                                    from mensagens import MensagensStatus
                                    MensagensStatus.temporario_principal(outer_context, _tr("zoom.display").format(factor=f"{z:.1f}"), 1500)
                            except Exception:
                                pass
                            event.accept()
                            return
                except Exception:
                    pass
                super().keyPressEvent(event)

        view = AmadonWebView()
        view.setHtml(full_html)
        self.inject_widget(view, target=target, clear=clear)

        if on_load_js:
            # Executa JS adicional após load completo.
            def _run_js():
                try:
                    view.page().runJavaScript(on_load_js)
                except Exception:
                    pass
            # Hook simples utilizando loadFinished
            try:
                view.loadFinished.connect(lambda _ok: _run_js())  # type: ignore
            except Exception:
                pass
        return view

    def inject_markdown(
        self,
        markdown_text: str,
        target: str = 'left',
        clear: bool = True,
        css: str | None = None,
        use_bootstrap: bool = True,
        extras: list[str] | None = None,
    ):
        """Converte markdown em HTML e injeta via WebEngine (ou QTextBrowser fallback).

        Parameters
        ----------
        markdown_text : str
            Texto em markdown.
        target : str
            'left' ou 'right'.
        clear : bool
            Limpa painel antes de inserir.
        css : str | None
            CSS adicional inline.
        use_bootstrap : bool
            Se True, carrega Bootstrap (facilita estilos prontos).
        extras : list[str] | None
            Lista de extras passados para markdown2 (fenced-code-blocks, tables etc.).
        """
        html_fragment: str
        extras = extras or [
            "fenced-code-blocks",
            "tables",
            "strike",
            "footnotes",
            "metadata",
            "task_list",
        ]
        try:
            import markdown2  # type: ignore
            html_fragment = markdown2.markdown(markdown_text, extras=extras)  # type: ignore
        except Exception:
            # Fallback extremamente simples
            paras = '\n'.join(f'<p>{p}</p>' for p in markdown_text.splitlines() if p.strip())
            html_fragment = f"<div class='md-fallback'>{paras}</div>"
        body = f"<div class='markdown-body'>{html_fragment}</div>"
        # CSS adaptativo para markdown respeitando classes de tema já definidas em inject_web_content
        default_css = (
            """
            .markdown-body { line-height:1.55; font-size:14px; }
            .markdown-body h1 { font-size:1.9em; margin:0.5em 0 0.6em; }
            .markdown-body h2 { font-size:1.48em; margin:1.2em 0 0.55em; }
            .markdown-body h3 { font-size:1.18em; margin:1em 0 0.45em; }
            body.doc-theme-light .markdown-body pre { background:#f5f7fa; color:#1d1d1d; border:1px solid #d0d7e2; }
            body.doc-theme-dark .markdown-body pre { background:#272822; color:#eee; border:1px solid #3a3f42; }
            body.doc-theme-light .markdown-body code { background:#f0f2f5; color:#222; }
            body.doc-theme-dark .markdown-body code { background:#1e1e1e; color:#eee; }
            .markdown-body pre { padding:8px 10px; border-radius:6px; overflow:auto; font-size:0.92em; }
            .markdown-body code { padding:2px 4px; border-radius:4px; }
            .markdown-body table { border-collapse:collapse; margin:1em 0; }
            body.doc-theme-light .markdown-body table th, body.doc-theme-light .markdown-body table td { border:1px solid #c7d4e5; }
            body.doc-theme-dark .markdown-body table th, body.doc-theme-dark .markdown-body table td { border:1px solid #3a3f42; }
            .markdown-body table th, .markdown-body table td { padding:6px 10px; font-size:0.92em; }
            .markdown-body blockquote { margin:1em 0; padding:8px 14px; border-left:4px solid #1565c0; border-radius:4px; }
            body.doc-theme-light .markdown-body blockquote { background:#f0f5fb; }
            body.doc-theme-dark .markdown-body blockquote { background:#1e1e24; border-left-color:#90caf9; }
            """
        )
        merged_css = (default_css + (css or "")) if css else default_css
        return self.inject_web_content(body, target=target, clear=clear, css=merged_css, use_bootstrap=use_bootstrap)

    @abstractmethod
    def GenerateData(self) -> str:  # noqa: N802
        """Executa a ação e retorna representação textual (diagnóstico)."""
        raise NotImplementedError

    # Novo método Show para exibir componentes modais (default: no-op)
    def Show(self):  # noqa: N802
        pass
