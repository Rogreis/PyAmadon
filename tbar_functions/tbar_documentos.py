from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _
from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
    QWidget,
    QVBoxLayout,
)
from pathlib import Path
from app_settings import settings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from document_resolver import resolve_doc_link

class ToolBar_Documentos(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.documentos")
        self._status_curto("status.curto.doc")
        self._status_principal("status.msg.documentos")
        base = Path(__file__).resolve().parent.parent
        css_path = base / 'assets' / 'css' / 'documentos.css'
        js_path = base / 'assets' / 'js' / 'documentos.js'
        tree_json = base / 'assets' / 'data' / 'documentos_tree.json'
        try:
            css_external = css_path.read_text(encoding='utf-8')
        except Exception:
            css_external = "body{font-family:Segoe UI,Arial,sans-serif;}"
        try:
            js_external = js_path.read_text(encoding='utf-8')
        except Exception:
            js_external = "console.warn('documentos.js não encontrado');"

        # Container com filtro + árvore
        container = QWidget()
        vlayout = QVBoxLayout(container)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(4)

        filtro = QLineEdit()
        filtro.setPlaceholderText(_("filter.placeholder.documentos"))
        filtro.setClearButtonEnabled(True)
        vlayout.addWidget(filtro)

        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        vlayout.addWidget(tree, 1)

        # Estilos tema claro / escuro
        if settings.dark_mode:
            tree.setStyleSheet(
                "QTreeWidget { background:#1e1e1e; border:1px solid #3a3f45; color:#e0e0e0; }"
                "QTreeView::item { padding:2px 4px; }"
                "QTreeView::item:selected { background:#264f78; color:#ffffff; }"
            )
        else:
            tree.setStyleSheet(
                "QTreeWidget { background:#ffffff; border:1px solid #c7d4e5; color:#222; }"
                "QTreeView::item { padding:2px 4px; }"
                "QTreeView::item:selected { background:#1565c0; color:#fff; }"
            )

        import json, os

        # Cache simples baseado em mtime
        cls = self.__class__
        if not hasattr(cls, '_cache_data'):
            cls._cache_data = None  # type: ignore[attr-defined]
            cls._cache_mtime = None  # type: ignore[attr-defined]

        mtime = None
        try:
            mtime = tree_json.stat().st_mtime
        except Exception:
            pass

        if getattr(cls, '_cache_data') is None or getattr(cls, '_cache_mtime') != mtime:
            try:
                data = json.loads(tree_json.read_text(encoding='utf-8'))
            except Exception:
                data = {"nodes": []}
            setattr(cls, '_cache_data', data)
            setattr(cls, '_cache_mtime', mtime)
        else:
            data = getattr(cls, '_cache_data')

        style = QApplication.instance().style() if QApplication.instance() else None

        def add_nodes(parent_item, nodes, level=0):
            for n in nodes:
                titulo = n.get("titulo", "(sem título)")
                item = QTreeWidgetItem([titulo])
                item.setData(0, 32, n.get("link"))  # Qt.UserRole = 32
                # Ícones simples por nível
                if style:
                    if level == 0:
                        item.setIcon(0, style.standardIcon(style.StandardPixmap.SP_DirIcon))
                    elif level == 1:
                        item.setIcon(0, style.standardIcon(style.StandardPixmap.SP_FileDialogListView))
                    else:
                        item.setIcon(0, style.standardIcon(style.StandardPixmap.SP_FileIcon))
                if parent_item:
                    parent_item.addChild(item)
                else:
                    tree.addTopLevelItem(item)
                filhos = n.get("filhos")
                if filhos:
                    add_nodes(item, filhos, level + 1)

        add_nodes(None, data.get("nodes", []))
        tree.expandToDepth(1)

        # Evento de clique: atualiza painel direito com detalhes do nó
        def on_item_clicked(item: QTreeWidgetItem):
            titulo = item.text(0)
            link = item.data(0, 32) or "(sem link)"
            # Esquema 'doc://' é lógico, usado para mapear futuramente a um
            # repositório de textos (ex.: carregar conteúdo real do documento).
            # Aqui apenas exibimos o identificador; uma evolução pode resolver
            # doc://parte1/sec2/doc3 -> buscar texto em banco/arquivo.
            # Log custom por nó
            try:
                from mensagens import AmadonLogging
                AmadonLogging.info(self.context, _("log.open.documentos.node").format(link=link))
            except Exception:
                pass
            resolved = resolve_doc_link(str(link))
            body = f"""
            <div class='container py-3'>
                <h2>{titulo}</h2>
                <p class='text-muted small mb-2'>ID lógico: <code>{link}</code></p>
                <div class='mb-3 doc-content'>{resolved}</div>
                <button id='btnCount' class='btn btn-primary btn-sm'>Clique para contar <span class='badge text-bg-light' id='ctr'>0</span></button>
                <hr/>
                <p class='footer-note text-secondary'>Renderizado em tempo real. Markdown suportado.</p>
            </div>
            """
            # Limpa painel direito antes de inserir novo HTML
            self.inject_web_content(body, target='right', clear=True, use_bootstrap=True, css=css_external, js=js_external)

        tree.itemClicked.connect(on_item_clicked)  # type: ignore

        # Filtro
        def apply_filter(text: str):
            pattern = text.strip().lower()
            def match_item(it: QTreeWidgetItem):
                # Se algum filho visível, mantém pai
                child_match = False
                for i in range(it.childCount()):
                    child = it.child(i)
                    child_visible = match_item(child)
                    child_match = child_match or child_visible
                own = pattern in it.text(0).lower() if pattern else True
                visible = own or child_match
                it.setHidden(not visible)
                return visible
            for i in range(tree.topLevelItemCount()):
                match_item(tree.topLevelItem(i))
        filtro.textChanged.connect(apply_filter)  # type: ignore
        # Injeta árvore no painel esquerdo
        self.inject_widget(container, target='left', clear=True)
        # Página inicial direita (mensagem introdutória)
        intro_body = f"""
        <div class='container py-3'>
            <h2>{_("html.doc.title")}</h2>
            <p class='lead'>{_("html.doc.intro")}</p>
            <p>Selecione um nó da árvore à esquerda para ver detalhes.</p>
        </div>
        """
        self.inject_web_content(intro_body, target='right', clear=True, use_bootstrap=True, css=css_external, js=js_external)
        return _("status.msg.documentos")