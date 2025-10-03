from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from i18n import _
from PySide6.QtWidgets import QWidget, QTextBrowser, QScrollArea, QVBoxLayout

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

        head_parts: list[str] = []
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

        full_html = (
            "<html><head>"
            + "".join(head_parts)
            + "</head><body>"
            + body_html
            + "".join(script_tail)
            + "</body></html>"
        )

        view = QWebEngineView()
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
        default_css = (
            """
            .markdown-body { line-height:1.5; font-size:14px; }
            .markdown-body h1,h2,h3 { margin-top:1.2em; font-weight:600; }
            .markdown-body pre { background:#272822; color:#eee; padding:8px; border-radius:6px; overflow:auto; }
            .markdown-body code { background:#eee; padding:2px 4px; border-radius:3px; }
            .markdown-body table { border-collapse:collapse; }
            .markdown-body table th, .markdown-body table td { border:1px solid #ccc; padding:4px 8px; }
            """
        )
        merged_css = (default_css + (css or "")) if css else default_css
        return self.inject_web_content(body, target=target, clear=clear, css=merged_css, use_bootstrap=use_bootstrap)

    @abstractmethod
    def GenerateData(self) -> str:  # noqa: N802
        """Executa a ação e retorna representação textual (diagnóstico)."""
        raise NotImplementedError
